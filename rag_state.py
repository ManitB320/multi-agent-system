import os, pickle
from dotenv import load_dotenv
import google.generativeai as genai
# REMOVED: from sentence_transformers import SentenceTransformer 
import faiss
import numpy as np

# Load environment variables once
load_dotenv()

# --- Global State Dictionary ---
RAG_STATE = {
    "embedding_model": None, # Now stores the genai Client
    "synthesis_model": None,
    "faiss_index": None,
    "data_store": None
}

# --- Lazy Loaders ---

def get_synthesis_model():
    """Initializes and returns the Gemini Synthesis Model only once."""
    if RAG_STATE["synthesis_model"] is None:
        print("--- RAG_STATE: Initializing Gemini Synthesis Model... ---")
        # Ensure API key is configured before creating the model
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        RAG_STATE["synthesis_model"] = genai.GenerativeModel("gemini-2.5-flash")
        print("--- RAG_STATE: Gemini Synthesis Model loaded. ---")
    return RAG_STATE["synthesis_model"]

def get_embedding_client():
    """Initializes and returns the configured genai client for API calls."""
    if RAG_STATE["embedding_model"] is None:
        print("--- RAG_STATE: Initializing lightweight Gemini Client for Embeddings... ---")
        # The client itself is lightweight and manages the API calls
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        RAG_STATE["embedding_model"] = genai.Client()
        print("--- RAG_STATE: Embedding Client loaded. ---")
    return RAG_STATE["embedding_model"]

def load_faiss_index_data(db_path="pdf_store"):
    """Loads FAISS index and data (chunks/metadata) only if not loaded."""
    if RAG_STATE["faiss_index"] is None or RAG_STATE["data_store"] is None:
        index_file = f"{db_path}/index.faiss"
        data_file = f"{db_path}/data.pkl"
        
        if os.path.exists(index_file) and os.path.exists(data_file):
            print("--- RAG_STATE: Loading FAISS Index and Data Store... ---")
            try:
                RAG_STATE["faiss_index"] = faiss.read_index(index_file)
                RAG_STATE["data_store"] = pickle.load(open(data_file, "rb"))
                print("--- RAG_STATE: FAISS and Data loaded successfully. ---")
            except Exception as e:
                print(f"--- RAG_STATE ERROR: Failed to load FAISS/Data: {e} ---")
        else:
            print("--- RAG_STATE: FAISS files not found. They will be loaded/created upon PDF upload/query. ---")
            
    # Return the current state (can be None if files don't exist yet)
    return RAG_STATE["faiss_index"], RAG_STATE["data_store"]