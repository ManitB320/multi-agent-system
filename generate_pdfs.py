from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

# Create folder if it doesn't exist
os.makedirs("sample_pdfs", exist_ok=True)

# Each document will have a title and some dummy text
docs = {
    "NebulaByte_AI_Strategy_Report.pdf": """
    NebulaByte's AI Division has developed a multi-agent architecture designed
    to enable autonomous collaboration between generative AI systems and retrieval
    modules. The current focus is on optimizing retrieval augmentation and 
    decision routing. The project highlights include integration of FAISS-based
    knowledge stores, adaptive controller agents, and secure API-driven pipelines.
    """,

    "NebulaByte_Meeting_Notes_Q1.pdf": """
    Meeting Summary: The AI Research team discussed deployment of the new
    decision-making pipeline. Tasks were assigned to improve PDF RAG ingestion
    efficiency and refine model selection logic. Security concerns were raised
    regarding API key management and cloud storage of embeddings.
    """,

    "NebulaByte_Product_Overview.pdf": """
    NebulaByte offers a suite of intelligent automation tools powered by 
    natural language processing and reinforcement learning. Core modules include
    the Insight Engine, Smart RAG Processor, and ArXiv Paper Summarizer.
    These systems help businesses turn unstructured data into actionable insights.
    """,

    "NebulaByte_Tech_Research_Summary.pdf": """
    Research Summary: Recent experiments compared sentence-transformer models
    for text embedding quality. Results showed 'all-MiniLM-L6-v2' as an optimal
    balance between speed and semantic accuracy. Future work involves fine-tuning
    domain-specific embeddings for industrial data applications.
    """,

    "NebulaByte_CEO_Update.pdf": """
    CEO Message: NebulaByte continues to expand its AI research partnerships.
    This quarter saw collaborations with academic institutions for
    multi-agent orchestration research and secure AI pipelines. The next
    milestone is deploying an end-to-end demo integrated with FastAPI
    and cloud-hosted FAISS vector stores.
    """
}

# Generate the PDFs
for filename, text in docs.items():
    path = os.path.join("sample_pdfs", filename)
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, filename.replace(".pdf", ""))
    text_lines = text.strip().split("\n")
    y = height - 120
    for line in text_lines:
        c.drawString(50, y, line.strip())
        y -= 20
    c.save()

print("5 NebulaByte sample PDFs generated successfully in 'sample_pdfs/' folder.")
