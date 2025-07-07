from supabase import create_client
import json
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)


def create_embeddings(text):
    response = supabase.functions.invoke("create-embedding", 
                                        invoke_options={"body": {"text": text}})

    embedding = json.loads(response.decode('utf-8'))

    return embedding

def similarity_search(query_text, document_text_id, top_k=3):
    query_embedding = create_embeddings(query_text)
    response = supabase.rpc(
        "match_vectors",
        {
            "query_embedding": query_embedding,
            "match_count": top_k,
            "document_text_id": document_text_id,
        }
    ).execute()
    
    return response.data

# Example usage:
response = similarity_search('What are the main ideas?', document_text_id="p6ZDpLW2VHDtwI3nq8Oxu", top_k=3)

print(response)