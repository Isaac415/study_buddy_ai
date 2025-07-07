import os, json
from dotenv import load_dotenv
# LangGraph imports
from langgraph.prebuilt import InjectedState
from typing import Annotated
from langchain_core.tools import tool

# Supabase
from supabase import create_client

# Django imports
from core.models import Course, Document


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
        documents = Document.objects.filter(user_id=request.user.id)
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
        documents = Document.objects.filter(user_id=request.user.id, course=course)
    except:
        return "Directly tell the user cannot find documents for this course."
    
    document_list = list()
    for document in documents:
        document_list.append(document.__dict__)

    return document_list

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
        document = Document.objects.get(user_id=request.user.id, original_filename=document_name)
    except:
        return "Directly tell the user cannot find such document"
    
    # Initialize Supabase Client
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    supabase = create_client(url, key)

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


toolbox = [
    # Basic
    get_user_email, 
    get_user_all_courses, 
    get_user_all_documents,
    get_documents_given_course,

    # RAG
    retrieve_document_info_given_query,
    
    ]