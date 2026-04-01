import os
from pinecone import Pinecone
from services.embeddings import get_embeddings  # <-- NEW IMPORT
from dotenv import load_dotenv

load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("restaurant-reviews")

def perform_semantic_search(query, top_k=3):
    """
    The main search function used by your UI.
    """
    # 1. Turn the user's search query into a vector using our shared service
    query_vector = get_embeddings(query) 
    
    if query_vector is None or not isinstance(query_vector, list):
        print("⏭️ Skipping search: Model is likely still loading on Hugging Face.")
        return [] # Return empty results so the UI doesn't crash

    # 2. Query Pinecone for the closest matches
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )
    
    # 3. Format results for the Streamlit UI
    matches = []
    for match in results['matches']:
        matches.append({
            "name": match['metadata']['name'],
            "cuisine": match['metadata']['cuisine'],
            "review": match['metadata']['review'],
            "score": round(match['score'] * 100, 2)
        })
    return matches