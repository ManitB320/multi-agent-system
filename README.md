# 🤖 Multi-Agent Retrieval-Augmented Generation (RAG) System

This project is a multi-agent orchestration framework built on **FastAPI** and the **Gemini API**. It features an intelligent **Controller Agent** that dynamically routes user queries to specialized agents, including a citation-aware PDF RAG system, a Web Search agent, and an Arxiv Search agent.

## ✨ Features

- **LLM-Powered Routing:** A Controller Agent (using Gemini) decides which specialized agents (`PDF_RAG`, `Web_Search`, `Arxiv_Search`) to activate based on the query's intent.
- **Advanced PDF RAG:** Uses `PyMuPDF`, `sentence-transformers`, `langchain-text-splitters`, and `FAISS` for robust, chunked, and metadata-rich internal knowledge retrieval.
- **Source Citation:** The PDF RAG agent is engineered to return answers with precise `[Source: filename, Page: X]` citations.
- **Real-Time Logging:** Full query trace, agent decisions, and retrieved context chunks are logged to a `logs/trace.json` file and displayed on the frontend.
- **Frontend Demo:** A simple HTML/CSS/JS interface to interact with the API endpoints.

## Setup and Run

### 1. Prerequisites

- Python 3.9+
- A **Google Gemini API Key**.

### Environment Setup

Clone the repository and install the dependencies:

```bash
pip install -r requirements.txt
```

##  API Key Configuration

1. Create a file named .env in the root directory.
2. Add your API key:
```bash
# .env
GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```
## Generate Sample Data

Run the utility script to create internal PDF documents for the RAG agent:
```bash
python generate_pdfs.py
```
This populates the sample_pdfs/ folder.

## Start the Server

Start the FastAPI application:
```bash
# .env
# The server runs on [http://127.0.0.1:8000](http://127.0.0.1:8000)
uvicorn main:app --reload
```

###  How to Use

1. Open the Frontend: Navigate to frontend/index.html in your web browser.

2. Ingest PDFs: Before querying, use the "Upload PDF" button to ingest the sample documents from the sample_pdfs/ folder. This builds   the internal FAISS vector store.

3. Ask a Query: Enter a question in the "Ask me something..." box. The system will automatically route the query to the correct agent(s).

4. Check Logs: The "Logs" section provides a detailed trace of the agent decision process.