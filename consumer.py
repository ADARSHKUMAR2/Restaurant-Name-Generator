import os
import requests
from dotenv import load_dotenv

load_dotenv()

# The canonical 2026 router URL: model ID first, pipeline instruction second
HF_API_URL = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"
HF_HEADERS = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}

def get_embeddings(text):
    """Calls Hugging Face API to extract a vector embedding."""
    try:
        # Reverting to the standard inference payload
        payload = {"inputs": text}
        
        response = requests.post(HF_API_URL, headers=HF_HEADERS, json=payload)
        
        # 1. Catch non-200 responses
        if response.status_code != 200:
            print(f"⚠️ Hugging Face API Error: Status {response.status_code}")
            print(f"   Raw Content: {response.text}")
            return None

        result = response.json()

        # 2. Handle Model Loading/API Errors 
        if isinstance(result, dict) and "error" in result:
            print(f"⚠️ Hugging Face is warming up: {result['error']}")
            return None 

        # 3. Handle Nested Lists
        if isinstance(result, list) and len(result) > 0:
            if isinstance(result[0], list):
                return result[0] 
            return result 
            
        print("⚠️ Unexpected JSON structure from Hugging Face.")
        return None
        
    except Exception as e:
        print(f"❌ Embedding Error Details: {e}")
        return None