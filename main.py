from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware 
import agents.controller as controller
import uvicorn
import json, os 
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

app = FastAPI(title = "multi-agent-system")

#Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for local dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
async def ask(query: str):
    response, logs = await controller.route_query(query)

    return {"query": query, "response": response, "logs": logs}

@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    os.makedirs("pdfs", exist_ok = True)
    file_path = f"pdfs/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    from agents.pdf_agent import process_pdf, embed_text, build_faiss_index

    text = process_pdf(file_path)
    chunks, emb = embed_text(text)
    build_faiss_index(chunks, emb)

    return {"filename": file.filename, "status": "PDF processed and indexed"}
    
@app.get("/logs")
async def get_logs():
    log_path = "logs/trace.json"

    #Ensure logs file exists

    if not os.path.exists(log_path):
        return {"logs": []}

    try:
        with open(log_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        data = []

    return {"logs": data}

if __name__ == "__main__":
    uvicorn.run("main:app", host = "0.0.0.0", port = 8000, reload = True)