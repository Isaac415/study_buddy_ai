import os, json
from dotenv import load_dotenv

# LangGraph imports
from langgraph.prebuilt import InjectedState
from typing import Annotated
from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_deepseek import ChatDeepSeek

# Supabase
from supabase import create_client

def supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    supabase = create_client(url, key)

    return supabase

# Django imports
from core.models import Course, MultipleChoiceQuestion
from core.models import Document as DjangoDocument


@tool
def get_user_email(state: Annotated[dict, InjectedState]):
    '''
    This tool gives the email address of the current user.
    '''
    request = state["request"]
    return request.user.email

@tool
def get_user_all_courses(state: Annotated[dict, InjectedState]):
    '''
    This tool gives a (python) list of courses of the current user. Each course has the following attributes/columns:
    id, name, description, user, color, and created_at.
    If the user queries about the course, you only have to give the name and description of each course.
    '''
    request = state['request']

    try:
        courses = Course.objects.filter(user_id=request.user.id)
    except:
        return "Directly tell the user he/she has no course."

    course_list = list()
    for course in courses:
        course_list.append(course.__dict__)

    return course_list

@tool
def get_user_all_documents(state: Annotated[dict, InjectedState]):
    '''
    This tool gives a (python) list of documents of the current user. Each document has the following attributes/columns: 
    id, description, url, created_at, course_id, user_id, and original_filename.
    If the user queries about the document, you only have to give the original_filename and description of each document.
    '''
    request = state['request']
    try:
        documents = DjangoDocument.objects.filter(user_id=request.user.id)
    except:
        return "Directly tell the user he/she has no document."

    document_list = list()
    for document in documents:
        document_list.append(document.__dict__)

    return document_list

@tool
def get_documents_given_course(state: Annotated[dict, InjectedState], course_name: str):
    '''
    This tool gives a (python) list of documents given a course. Each document has the following attributes/columns: 
    id, description, url, created_at, course_id, user_id, and original_filename.

    Only show user the original filename (just call it filename) and description.
    Parameter: course_name - str: the name column value of a Course object / provided by the user.
    '''
    request = state['request']
    try:
        course = Course.objects.get(user_id=request.user.id, name=course_name)
    except:
        return "Directly tell the user cannot find the course provided."
    
    try:
        documents = DjangoDocument.objects.filter(user_id=request.user.id, course=course)
    except:
        return "Directly tell the user cannot find documents for this course."
    
    document_list = list()
    for document in documents:
        document_list.append(document.__dict__)

    return document_list


@tool
def get_document_content(state: Annotated[dict, InjectedState], document_name):
    '''
    This tool gives the whole document text content. This information can be used to generate summary for the whole document.
    '''
    # Initialize Supabase Client
    supabase = supabase_client()
    return

@tool
def retrieve_document_info_given_query(state: Annotated[dict, InjectedState], query, document_name):
    '''
    This tool gives the highest 3 similariy chunks for retrieval-augmented generation given the user query and document name. If the chunks do not contain the information the user asked for, tell the user the document does not contain such information.
    Parameters:
    query - the question user asked about the document
    document_name - the original_filename column of the document object
    '''
    request = state["request"]
    try:
        document = DjangoDocument.objects.get(user_id=request.user.id, original_filename=document_name)
    except:
        return "Directly tell the user cannot find such document"
    
    # Initialize Supabase Client
    supabase = supabase_client()

    # Create embeddings of the query
    response = supabase.functions.invoke("create-embedding", 
                                        invoke_options={"body": {"text": query}})
    embedding = json.loads(response.decode('utf-8'))
    
    # Get chunks
    response = supabase.rpc(
        "match_vectors",
        {
            "query_embedding": embedding,
            "match_count": 3,
            "document_text_id": document.id,
        }
    ).execute()

    return response.data

def summarize_file(file_path: str) -> str:
    load_dotenv()

    # Extract text
    pdf_loader = PyPDFLoader(file_path)
    pages = pdf_loader.load()
    large_text = "".join(page.page_content for page in pages)
    
    # Split text into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_text(large_text)
    documents = [Document(page_content=text) for text in texts]

    
    # Initialize LLM
    llm = ChatDeepSeek(model="deepseek-chat")
    
    # Define prompt
    stuff_prompt = PromptTemplate.from_template("Summarize this text in 5-6 sentences: {context}")
    
    # Set up stuff chain
    stuff_chain = create_stuff_documents_chain(llm, stuff_prompt)
    
    # Run summarization
    return stuff_chain.invoke({"context": documents})


@tool
def create_document_summary(state: Annotated[dict, InjectedState], document_name):
    '''
    This tool returns a summary of the document.
    Parameters:
    document_name - original_filename of the document
    '''
    request = state["request"]
    try:
        document = DjangoDocument.objects.get(user_id=request.user.id, original_filename=document_name)
        local_path = f"./temp/{document.url}"
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
    except:
        return "Directly tell the user cannot find such document"
    
    # Download the document
    supabase = supabase_client()
    with open(local_path, "wb+") as f:
        response = (
            supabase.storage
            .from_("user-uploads")
            .download(document.url)
        )
        f.write(response)

    try:
        summary = summarize_file(local_path)
    finally:
        # Always attempt to delete the file, even if summarization fails
        if os.path.exists(local_path):
            os.remove(local_path)

    return summary

def generate_mcq(file_path: str, num_of_mcq) -> str:
    load_dotenv()

    # Extract text
    pdf_loader = PyPDFLoader(file_path)
    pages = pdf_loader.load()
    large_text = "".join(page.page_content for page in pages)
    
    # Split text into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_text(large_text)
    documents = [Document(page_content=text) for text in texts]

    
    # Initialize LLM
    llm = ChatDeepSeek(model="deepseek-chat")
    
    # Define prompt
    stuff_prompt = PromptTemplate.from_template("Generate {num_of_mcq} quiz(zes) from this text: {context}. Each multiple choice question should have 4 choices. Also give the correct answer. Try to keep your response in this format: [q1: str, q1c1: str, q1c2: str, q1c3: str, q1c4: str, q1ans: int], [q2: str, q2c1: str, q2c2: str, q2c3: str, q2c4: str, q2ans: int], ...")
    
    # Set up stuff chain
    stuff_chain = create_stuff_documents_chain(llm, stuff_prompt)
    
    # Run summarization
    return stuff_chain.invoke({"num_of_mcq": num_of_mcq, "context": documents})

@tool
def create_multiple_choice_questions_given_document(state: Annotated[dict, InjectedState], document_name: str, num_of_mcq: int):
    '''
    This tool returns some multiple choice questions.
    Parameters:
    document_name: str - original_filename of the document
    num_of_mcq: int - the number of multiple choice this tool should generate
    '''
    request = state["request"]
    try:
        document = DjangoDocument.objects.get(user_id=request.user.id, original_filename=document_name)
        local_path = f"./temp/{document.url}"
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
    except:
        return "Directly tell the user cannot find such document"
    
    # Download the document
    supabase = supabase_client()
    with open(local_path, "wb+") as f:
        response = (
            supabase.storage
            .from_("user-uploads")
            .download(document.url)
        )
        f.write(response)

    try:
        mcqs = generate_mcq(local_path, num_of_mcq)
    finally:
        # Always attempt to delete the file, even if summarization fails
        if os.path.exists(local_path):
            os.remove(local_path)

    return mcqs

@tool
def save_multiple_choice_question(state: Annotated[dict, InjectedState], 
                                  document_name: str,
                                  question: str,
                                  choice_1: str,
                                  choice_2: str,
                                  choice_3: str,
                                  choice_4: str,
                                  correct_ans: int):
    '''
    This tool will save one single multiple choice question into the database
    Parameters:
    document_name: str - original_filename of the document
    choice_1, choice_2, choice_3, choice_4: str - the four choices of the question
    correct_ans: int - the correct answer of the question
    '''
    request = state["request"]
    try:
        document = DjangoDocument.objects.get(user_id=request.user.id, original_filename=document_name)
    except:
        return "Directly tell user and error has occured and please try again"
    
    question = MultipleChoiceQuestion.objects.create(
        user=request.user, 
        document=document, 
        question=question, 
        choice_1=choice_1,
        choice_2=choice_2,
        choice_3=choice_3,
        choice_4=choice_4,
        correct_ans=correct_ans,
    )

    return f"Successfully saved question: {question}"



toolbox = [
    # Basic
    get_user_email, 
    get_user_all_courses, 
    get_user_all_documents,
    get_documents_given_course,

    # RAG
    retrieve_document_info_given_query,
    create_document_summary,
    create_multiple_choice_questions_given_document,
    save_multiple_choice_question,
    ]