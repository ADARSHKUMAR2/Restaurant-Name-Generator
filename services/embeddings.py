import os
import requests
from dotenv import load_dotenv

load_dotenv()

# We now use the standard OpenAI-compatible v1/embeddings endpoint
HF_API_URL = "https://router.huggingface.co/hf-inference/v1/embeddings"
HF_HEADERS = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}

def get_embeddings(text):
    """Calls Hugging Face API using the standard v1 embeddings endpoint."""
    try:
        # The payload explicitly defines the model and input text
        payload = {
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "input": text
        }
        
        response = requests.post(HF_API_URL, headers=HF_HEADERS, json=payload)
        
        # 1. Catch non-200 responses
        if response.status_code != 200:
            print(f"⚠️ Hugging Face API Error: Status {response.status_code}")
            print(f"   Raw Content: {response.text}")
            return None

        result = response.json()

        # 2. Parse the clean OpenAI-style response
        if "data" in result and len(result["data"]) > 0:
            # This directly extracts the flat list of floats
            return result["data"][0]["embedding"] 
            
        print("⚠️ Unexpected JSON structure from Hugging Face.")
        return None
        
    except Exception as e:
        print(f"❌ Embedding Error Details: {e}")
        return None