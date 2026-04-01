import os
from pinecone import Pinecone
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

# Load environment variables (API keys)
load_dotenv()

# 1. Connect to Pinecone & Load the specific Hugging Face model
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("restaurant-reviews")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def perform_semantic_search(user_query, top_k=3):
    """
    Takes a plain text search, converts it to math, and finds the closest matches in Pinecone.
    Returns the top 3 best matching restaurants.
    """
    try:
        # Step A: Convert the user's search text into a 384-number vector
        query_vector = embeddings.embed_query(user_query)
        
        # Step B: Search Pinecone for the closest matching vectors
        search_results = index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True # We need this to get the name, cuisine, and review text back!
        )
        
        # Step C: Format the raw Pinecone data into a clean Python list
        formatted_results = []
        for match in search_results.get('matches', []):
            formatted_results.append({
                "id": match['id'],
                "score": match['score'], # A number between 0 and 1 indicating how close the match is
                "name": match['metadata']['name'],
                "cuisine": match['metadata']['cuisine'],
                "review": match['metadata']['review']
            })
            
        return formatted_results
        
    except Exception as e:
        print(f"Search Error: {e}")
        return []