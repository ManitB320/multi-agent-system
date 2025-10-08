# agents/pdf_agent.py (FULL FILE)
import os, re, pickle
import numpy as np
from pypdf import PdfReader
import faiss
from rag_state import get_synthesis_model, load_faiss_index_data, get_embedding_client

# Constants
DB_PATH = "pdf_store"

# Helper to build and save the index/data
def _build_and_save_index(chunks, metadata, embeddings):
    """Initializes FAISS index and saves it along with chunk data."""
    if not os.path.exists(DB_PATH):
        os.makedirs(DB_PATH)

    # 1. Build FAISS Index (IndexFlatL2 for L2/Euclidean distance)
    # The dimension is fixed by the gemini-embedding-001 model (3072)
    embedding_dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(embedding_dim)
    index.add(embeddings)

    # 2. Prepare Data Store (chunks and metadata)
    data_store = {
        "chunks": chunks,
        "metadata": metadata
    }

    # 3. Save to disk
    faiss.write_index(index, f"{DB_PATH}/index.faiss")
    pickle.dump(data_store, open(f"{DB_PATH}/data.pkl", "wb"))

# Helper for processing PDF and chunking
def _process_pdf_and_chunk(file_path: str):
    """Extracts text from PDF, cleans it, and chunks it for RAG."""
    reader = PdfReader(file_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    
    # Simple chunking by splitting large text into paragraphs/sections
    # You can enhance this with smarter splitters, but this is fast.
    chunks = [s.strip() for s in re.split(r'\n\n+|\r\n\r\n+', full_text) if s.strip()]
    metadata = [{"source": file_path, "chunk_id": i} for i, chunk in enumerate(chunks)]
    
    return chunks, metadata


# ---------- Ingestion Pipeline ----------

def ingest_pdf(file_path: str):
    """Reads a PDF, chunks it, generates embeddings, and saves the FAISS index."""
    
    # 1. Process PDF and Chunk Text
    print(f"Processing PDF file: {file_path}")
    chunks, metadata = _process_pdf_and_chunk(file_path)
    print(f"PDF split into {len(chunks)} chunks.")
        
    # 2. Generate Embeddings (NOW USES GEMINI API)
    print(f"Generating embeddings for {len(chunks)} chunks using Gemini API...")
    
    embedding_client = get_embedding_client() # Get the configured client
    
    # --- CRITICAL CHANGE: Use API Call for Indexing ---
    response = embedding_client.models.embed_content(
        model="gemini-embedding-001",
        contents=chunks,
        task_type="RETRIEVAL_DOCUMENT" 
    )
    embeddings = np.array(response['embeddings'])
    # --- END CRITICAL CHANGE ---
    
    # 3. Build and Save FAISS Index and Data
    _build_and_save_index(chunks, metadata, embeddings)
    print(f"Ingestion complete. Index saved to {DB_PATH}.")
    
    return True # Indicate success


# ---------- Agent Query Entry Point ----------

def handle_pdf_query(query: str):
    """
    Handles a user query:
    1. Loads the index/data.
    2. Embeds the query using Gemini API.
    3. Retrieves top chunks from FAISS.
    4. Uses Gemini to synthesize a summary based on the chunks.
    """
    
    # 1. Load FAISS Index and Data Store (Lazy Loading)
    index, data_store = load_faiss_index_data()
    if index is None:
        return "No PDF index found. Please upload a PDF first."

    # 2. Encode the query (NOW USES GEMINI API)
    embedding_client = get_embedding_client() # Get the configured client

    # --- CRITICAL CHANGE: Use API Call for Query Embedding ---
    query_response = embedding_client.models.embed_content(
        model="gemini-embedding-001",
        contents=[query], # Query must be in a list
        task_type="RETRIEVAL_QUERY" 
    )
    query_emb = np.array(query_response['embeddings'])
    # --- END CRITICAL CHANGE ---
    
    # 3. Retrieval step (k=3 for top 3 results)
    D, I = index.search(query_emb, 3) 
    
    retrieved_chunks = [data_store["chunks"][i] for i in I[0] if i != -1]
    
    if not retrieved_chunks:
        return f"Could not find relevant information in the PDF for the query: '{query}'."

    # 4. Synthesis with Gemini
    synthesis_model = get_synthesis_model()
    
    prompt = (
        "You are an expert document analyzer. Based ONLY on the following context, "
        "answer the user's question. If the context does not contain the answer, "
        "state that you cannot find the answer in the provided document. \n\n"
        "--- CONTEXT ---\n"
        f"{'\\n'.join(retrieved_chunks)}\n"
        "-----------------\n\n"
        f"USER QUESTION: {query}"
    )
    
    try:
        response = synthesis_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Synthesis Error: Failed to generate response from Gemini. Details: {e}"