from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

print("🧠 Loading AI Models (Llama 3.1 & Hugging Face)...")

llm = ChatGroq(model_name="llama-3.1-8b-instant") 
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def write_review(cuisine, name):
    """Uses Llama 3.1 to generate a creative review"""
    prompt = f"Write a vivid, 2-sentence food critic review for a {cuisine} restaurant named '{name}'."
    return llm.invoke(prompt).content

def generate_vector(text):
    """Converts English text into a mathematical array"""
    return embeddings.embed_query(text)