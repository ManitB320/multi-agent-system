# rag_state.py (NEW FILE at project root)
import os, pickle
from dotenv import load_dotenv
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import faiss

# Load environment variables once
load_dotenv()

# --- Global State Dictionary ---
RAG_STATE = {
    "embedding_model": None,
    "synthesis_model": None,
    "faiss_index": None,
    "data_store": None
}

# --- Lazy Loaders ---

def get_synthesis_model():
    """Initializes and returns the Gemini Synthesis Model only once."""
    if RAG_STATE["synthesis_model"] is None:
        print("--- RAG_STATE: Initializing Gemini Synthesis Model... ---")
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        RAG_STATE["synthesis_model"] = genai.GenerativeModel("gemini-2.5-flash")
        print("--- RAG_STATE: Gemini Model loaded. ---")
    return RAG_STATE["synthesis_model"]

def get_embedding_model():
    """Initializes and returns the Sentence Transformer Model only once."""
    if RAG_STATE["embedding_model"] is None:
        print("--- RAG_STATE: Initializing heavy SentenceTransformer model... ---")
        RAG_STATE["embedding_model"] = SentenceTransformer('all-MiniLM-L6-v2')
        print("--- RAG_STATE: Embedding Model loaded. ---")
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