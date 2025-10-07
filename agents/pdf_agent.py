import fitz # PyMuPDF
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os, pickle
from dotenv import load_dotenv
from google import generativeai as genai 

# --- LLM Generative Model (For synthesis) ---
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = "gemini-2.5-flash"
SYNTHESIS_MODEL = genai.GenerativeModel(MODEL_NAME) #Renamed for synthesis

# --- Embedding Model (For retrieval) ---
EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2') #Renamed for embedding
DB_PATH = "pdf_store"

def process_pdf(file_path):
    """Extracts all text from the PDF."""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def embed_text(text):
    """Chunks text and generates embeddings."""
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    # USE EMBEDDING_MODEL
    embeddings = EMBEDDING_MODEL.encode(chunks) 
    return chunks, np.array(embeddings)

def build_faiss_index(chunks, embeddings):
    """Builds and saves the FAISS index and text chunks."""
    os.makedirs(DB_PATH, exist_ok = True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    faiss.write_index(index, f"{DB_PATH}/index.faiss")
    pickle.dump(chunks, open(f"{DB_PATH}/chunks.pkl", "wb"))

def handle_pdf_query(query: str):
    """Performs RAG: Retrieves context and synthesizes an answer using the LLM."""
    
    if not os.path.exists(f"{DB_PATH}/index.faiss"):
        #Return dict for consistency with other agents
        return {"summary": "No PDF ingested yet. Upload one first.", "raw_results": []} 
        
    index = faiss.read_index(f"{DB_PATH}/index.faiss")
    chunks = pickle.load(open(f"{DB_PATH}/chunks.pkl", "rb"))
    
    # USE EMBEDDING_MODEL to encode the query
    query_emb = EMBEDDING_MODEL.encode([query]) 
    
    # Retrieval step
    D, I = index.search(query_emb, 5) 
    results = [chunks[i] for i in I[0]] # The raw chunks retrieved
    combined_context = " ".join(results)

    # --- LLM Synthesis Step ---
    prompt = f"""
    Based ONLY on the following context retrieved from an uploaded PDF, provide a concise and factual answer to the question: "{query}"

    Context:
    ---
    {combined_context}
    ---
    """
    
    try:
        #USE SYNTHESIS_MODEL to generate the answer (Sync call for the controller)
        response = SYNTHESIS_MODEL.generate_content(prompt)
        summary = response.text.strip()
    except Exception as e:
        #Fallback: return raw context with an error message
        summary = combined_context[:1000] + f"\n\n(Gemini summarization failed: {e})"
        
    #Return summary and raw results as a dictionary
    return {
        "summary": summary,
        "raw_results": results 
    }