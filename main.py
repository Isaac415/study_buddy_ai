from langchain.chains import LLMChain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_deepseek import ChatDeepSeek
from dotenv import load_dotenv

def summarize_file(file_path: str) -> str:
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


print(summarize_file('./temp/Isaac/1751992107_China History.pdf'))