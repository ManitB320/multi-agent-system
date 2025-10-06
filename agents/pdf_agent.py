import fitz
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os, pickle

model = SentenceTransformer('all-MiniLM-L6-v2')
DB_PATH = "pdf_store"

def process_pdf(file_path):

    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def embed_text(text):

    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    embeddings = model.encode(chunks)
    return chunks, np.array(embeddings)

def build_faiss_index(chunks, embeddings):
    os.makedirs(DB_PATH, exist_ok = True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    faiss.write_index(index, f"{DB_PATH}/index.faiss")
    pickle.dump(chunks, open(f"{DB_PATH}/chunks.pkl", "wb"))

def handle_pdf_query(query: str):
    
    if not os.path.exists(f"{DB_PATH}/index.faiss"):
        return "No PDF ingested yet. Upload one first."
    index = faiss.read_index(f"{DB_PATH}/index.faiss")
    chunks = pickle.load(open(f"{DB_PATH}/chunks.pkl", "rb"))
    query_emb = model.encode([query])
    D, I = index.search(query_emb, 3)
    results = [chunks[i] for i in I[0]]

    return " ".join(results)
