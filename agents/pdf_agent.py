import fitz # PyMuPDF
import numpy as np
import os, pickle
from dotenv import load_dotenv
from google import genai

# --- New Import for Advanced Chunking ---
from langchain_text_splitters import RecursiveCharacterTextSplitter 

# --- Configuration & Models ---
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# LLM Generative Model (For synthesis)
MODEL_NAME = "gemini-2.5-flash"
SYNTHESIS_MODEL = genai.GenerativeModel(MODEL_NAME) 

# Embedding Model (For retrieval)
from sentence_transformers import SentenceTransformer
EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2') 

# Vector Store/DB parameters
import faiss
DB_PATH = "pdf_store"

# --- RAG/Chunking Parameters ---
CHUNK_SIZE = 1000 
CHUNK_OVERLAP = 200 
SPLITTER_SEPARATORS = ["\n\n", "\n", " ", ""]


# ---------- Ingestion Pipeline (The New Logic) ----------

def ingest_pdf(file_path: str):
    """
    Handles the entire PDF ingestion pipeline:
    1. Extracts text page-by-page, with metadata.
    2. Chunks the text using recursive splitting.
    3. Embeds all chunks.
    4. Builds and saves the FAISS index and the associated data/metadata.
    """
    
    # 1. Process and Chunk
    print(f"Starting ingestion for {file_path}...")
    chunk_data_list = _process_pdf_and_chunk(file_path)
    if not chunk_data_list:
        print("Ingestion failed or no text found.")
        return
        
    # 2. Separate Data for Embedding and Saving
    chunks = [d["text"] for d in chunk_data_list]
    metadata = [d["metadata"] for d in chunk_data_list]

    # 3. Generate Embeddings
    print(f"Generating embeddings for {len(chunks)} chunks...")
    embeddings = EMBEDDING_MODEL.encode(chunks)
    
    # 4. Build and Save FAISS Index and Data
    _build_and_save_index(chunks, metadata, embeddings)
    print(f"Ingestion complete. Index saved to {DB_PATH}.")


def _process_pdf_and_chunk(file_path: str):
    """Internal function to handle PDF parsing and advanced chunking with metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=SPLITTER_SEPARATORS,
        length_function=len
    )
    
    final_chunks_data = []
    
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return []

    file_name = os.path.basename(file_path)
    
    for page_num, page in enumerate(doc):
        page_text = page.get_text()
        chunks = splitter.split_text(page_text)
        
        # Attach Metadata to each chunk
        for i, chunk in enumerate(chunks):
            chunk_data = {
                "text": chunk,
                "metadata": {
                    "source": file_name,
                    "page_number": page_num + 1,
                    "chunk_id": f"{file_name}_{page_num+1}_{i}",
                }
            }
            final_chunks_data.append(chunk_data)
            
    return final_chunks_data


def _build_and_save_index(chunks: list, metadata: list, embeddings: np.ndarray):
    """Internal function to build FAISS index and save the chunks + metadata."""
    
    os.makedirs(DB_PATH, exist_ok=True)
    
    # Save the index
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    faiss.write_index(index, f"{DB_PATH}/index.faiss")
    
    # Save the ENTIRE data structure (chunks and metadata)
    data_to_save = {"chunks": chunks, "metadata": metadata}
    pickle.dump(data_to_save, open(f"{DB_PATH}/data.pkl", "wb"))


# ---------- Agent Query Entry Point (for controller.py) ----------

def handle_pdf_query(query: str):
    """Performs RAG: Retrieves context including full metadata, and synthesizes an answer."""
    
    # Check for index and data file
    if not os.path.exists(f"{DB_PATH}/index.faiss") or not os.path.exists(f"{DB_PATH}/data.pkl"):
        return {"summary": "No PDF ingested yet. Upload one first.", "raw_results": []} 
        
    index = faiss.read_index(f"{DB_PATH}/index.faiss")
    data_store = pickle.load(open(f"{DB_PATH}/data.pkl", "rb"))
    all_chunks = data_store["chunks"]
    all_metadata = data_store["metadata"] # <--- CRITICAL: Now we have metadata!
    
    # Encode the query
    query_emb = EMBEDDING_MODEL.encode([query]) 
    
    # Retrieval step (k=5)
    D, I = index.search(query_emb, 5) 
    
    retrieved_chunks_with_meta = []
    combined_context = ""

    for chunk_index in I[0]:
        chunk = all_chunks[chunk_index]
        meta = all_metadata[chunk_index]
        
        # Format the context for the LLM to include the source citation
        context_citation = f"[Source: {meta['source']}, Page: {meta['page_number']}]"
        combined_context += f"{context_citation} {chunk}\n\n"
        
        # Store for the 'raw_results' return
        retrieved_chunks_with_meta.append({
            "text": chunk,
            "source": meta['source'],
            "page": meta['page_number']
        })

    # --- LLM Synthesis Step ---
    prompt = f"""
    You are an expert document summarizer. Your task is to provide a concise and factual answer to the question based ONLY on the context provided below.

    **CRITICAL INSTRUCTION:** You MUST include the full citation immediately following the sentence or fact they support. The citation format is always: [Source: filename, Page: X]. Do not generate citations if they are not present in the context.

    Question: "{query}"

    Context:
    ---
    {combined_context}
    ---
    """
    
    try:
        response = SYNTHESIS_MODEL.generate_content(prompt)
        summary = response.text.strip()
    except Exception as e:
        summary = f"**Summarization failed:** {e}. Raw context returned:\n\n{combined_context}"
        
    # Return summary and raw results (now with full metadata for logging)
    # The controller expects a list of text strings or a list of dicts it can parse.
    # We return the original text strings *with* the citation prepended for the logs.
    final_raw_results = [
        f"[Source: {d['source']}, Page: {d['page']}] {d['text']}" 
        for d in retrieved_chunks_with_meta
    ]

    return {
        "summary": summary,
        "raw_results": final_raw_results
    }