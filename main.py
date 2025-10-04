from fastapi import FastAPI, UploadFile, File
import agents.controller as controller
import uvicorn

app = FastAPI(title = "multi-agent-system")


@app.post("/ask")
async def ask(query: str):
    response, logs = controller.route_query(query)

    return {"query": query, "response": response, "logs": logs}

@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    # TODO : Add PDF ingestion to FAISS/Chroma
    return {"filename": file.filename, "status": "PDF uploaded successfully"}

@app.get("/logs")
async def get_logs():
    # TODO return saved logs from logs/trace.json
    return {"logs": []}

if __name__ == "__main__":
    uvicorn.run("main:app", host = "0.0.0.0", port = 8000, reload = True)