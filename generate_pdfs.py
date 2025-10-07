from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import textwrap

# Create folder if it doesn't exist
os.makedirs("sample_pdfs", exist_ok=True)

# --- Define the function to draw wrapped text (Unchanged from last fix) ---
def draw_wrapped_text(c, text, x, y_start, font_size, max_width):
    """
    Splits long text into lines based on max_width and draws them.
    Returns the final Y-coordinate after drawing.
    """
    # Define an estimated character limit based on font size and available width
    effective_width = max_width - x
    effective_width_chars = int(effective_width / (font_size * 0.6)) 

    leading = font_size + 4 
    y_position = y_start
    
    # Process each 'paragraph'
    for paragraph in text.strip().split('\n'):
        paragraph = paragraph.strip()
        if not paragraph:
            y_position -= leading
            continue

        # Use textwrap.wrap() to break the text at the character limit
        lines = textwrap.wrap(paragraph, width=effective_width_chars)
        
        # Draw each wrapped line
        for line in lines:
            # Ensure proper indentation/spacing is preserved by the wrapper
            c.drawString(x, y_position, line)
            y_position -= leading
            
        y_position -= (leading / 2) # Add half a line space between logical paragraphs

    return y_position

# --- EXPANDED, CLEANED CONTENT FOR RAG TESTING ---
docs = {
    "NebulaByte_AI_Strategy_Report.pdf": """
    Title: NebulaByte Multi-Agent Architecture and AI Strategy Report - 2025

    Section 1: The Adaptive Multi-Agent Paradigm
    NebulaByte's core AI division operates on a modular, multi-agent architecture (MAA) designed for highly autonomous decision-making and data processing. The MAA is governed by a central 'Controller Agent' responsible for task decomposition, tool/agent selection, and final synthesis. This agent utilizes a sophisticated LLM-based routing logic that dynamically selects one or more specialized agents (Web Search, ArXiv, PDF RAG) based on the user's query intent. This approach ensures maximal token efficiency and latency reduction. This system represents the future of enterprise knowledge management.

    Section 2: Retrieval Augmentation Mechanics
    The PDF RAG Agent is the cornerstone of our internal knowledge system. It employs a FAISS vector store deployed on a private cloud instance for fast, efficient nearest-neighbor search. Our ingestion pipeline uses the **sentence-transformers 'all-MiniLM-L6-v2' model** for generating embeddings, citing its superior performance-to-size ratio. The key retrieval setting is configured for **k=5** most relevant text chunks per query, ensuring a broad context is passed to the generation step, while also testing the LLM's ability to filter irrelevant noise. We've found that a chunk size of 500 characters works optimally for our specific data structure.

    Section 3: Future Optimizations
    The Q3 roadmap includes migrating the embedding model to a domain-specific fine-tuned variant to improve semantic search accuracy for industrial financial data. We are also researching techniques for hypothetical document embedding (HyDE) to further enhance retrieval for highly abstract or complex user queries. The success of the current FastAPI deployment framework has paved the way for a fully containerized, microservices-based agent deployment in Q4.
    """,

    "NebulaByte_Meeting_Notes_Q1.pdf": """
    Title: AI Research & Development Team Meeting Minutes - Q1/2025

    Attendees: Dr. A. Sharma (Lead Architect), E. Chen (DevOps), M. Patel (Security), J. Rios (RAG Specialist).
    Date: 2025-03-15
    Topic: Multi-Agent System Deployment Review

    Discussion Points:
    1. Deployment Pipeline: E. Chen reported the new asynchronous **FastAPI/Uvicorn pipeline** is stable under load testing, with an average query response time of 2.1 seconds. The primary dependency is the successful connection to the cloud-hosted FAISS index via a dedicated service endpoint at **192.168.1.44**.
    2. PDF RAG Ingestion: J. Rios highlighted that PDF ingestion efficiency needs refinement. The current chunking strategy occasionally splits critical facts, necessitating a move to a **recursive character splitting** approach with a **chunk overlap of 50 characters** to preserve context across boundaries.
    3. Security Review (M. Patel): **API Key management** remains a top security concern. All agent-specific keys (e.g., for external APIs or LLM providers) must be stored as **environment variables in a secure .env file** and injected at runtime, never hardcoded. Cloud storage of vector embeddings must be encrypted at rest using AES-256.
    4. Action Items:
        * E. Chen: Finalize the Docker deployment script for the controller service. Deadline: 2025-04-01.
        * J. Rios: Implement the **k=5 chunk retrieval** test case and report on synthesis quality.
        * M. Patel: Conduct a final audit of the .env file configuration against NebulaByte's security protocols by the end of the month.
    """,

    "NebulaByte_Product_Overview.pdf": """
    Title: NebulaByte Intelligent Automation Suite - Product Overview

    Our AI platform is a powerful blend of Natural Language Processing (NLP), sophisticated Multi-Agent Orchestration, and Reinforcement Learning (RL) models designed to transform enterprise data into actionable insights.

    Core Modules:
    * Insight Engine (IE-200): A state-of-the-art summarization and entity extraction tool. It utilizes a custom fine-tuned model for identifying key personnel and financial figures from dense legal and regulatory documents. It can process up to 100 documents per minute, with a 98% extraction accuracy rate.
    * Smart RAG Processor (SRP-300): The central Retrieval-Augmented Generation component. Its unique feature is its **adaptive k parameter**; it automatically adjusts the number of context chunks retrieved (k) based on the complexity score of the input query (from 3 for simple facts up to 7 for complex synthesis).
    * ArXiv Paper Summarizer: A specialized agent integrated with the SRP-300 that uses the DuckDuckGo Search tool to find recent academic papers, then generates a concise, 5-point summary. It is explicitly designed to handle niche topics involving **transformer models** and **graph neural networks (GNNs)**.

    Use Cases: Customers in the financial sector use the system for regulatory compliance checks, while the R&D team leverages its multi-source synthesis capability to compare internal research (PDFs) with the latest academic findings (ArXiv) to drive innovation.
    """,

    "NebulaByte_Tech_Research_Summary.pdf": """
    Title: Technical Deep Dive: Embedding Model Selection & Performance Benchmarks

    Executive Summary: This report details the evaluation of various sentence-transformer models for our RAG system's embedding layer, focusing on two key metrics: **semantic accuracy (mAP@10)** and **latency (ms per 1000 tokens)**.

    Model Benchmarks (Internal Data):
    * Model Name: all-MiniLM-L6-v2, Dimensionality: 384, mAP@10 Score: 0.82, Latency (ms/1000): 120, Conclusion: **Optimal Balance**
    * Model Name: all-MiniLM-L12-v2, Dimensionality: 384, mAP@10 Score: 0.84, Latency (ms/1000): 195, Conclusion: Higher latency, minimal gain
    * Model Name: GTE-small, Dimensionality: 768, mAP@10 Score: 0.86, Latency (ms/1000): 310, Conclusion: Highest accuracy, too slow for production

    Final Decision: We selected **'all-MiniLM-L6-v2'** as the default embedding model due to its optimal balance of retrieval quality (0.82) and speed. This choice directly impacts the system's Response Time metric, ensuring most queries are answered in under 3 seconds.

    Future Research: We are investigating the deployment of a **smaller, custom-distilled model** trained specifically on legal and technical documentation. Initial results suggest this could increase semantic accuracy to **0.88** for domain-specific queries without significantly impacting latency. This upgrade is tied to the Q4 production cycle, starting November 1st.
    """,

    "NebulaByte_CEO_Update.pdf": """
    Title: CEO Quarterly Address - Driving Next-Generation AI Innovation

    To our Employees and Partners,

    NebulaByte achieved significant strategic milestones this quarter, primarily driven by the success of our **Multi-Agent Orchestration** framework. The **FastAPI-powered** system represents a major leap in operationalizing complex AI workflows, offering unprecedented scalability and robustness for our enterprise clients. The company's stock symbol is **NBTX**, and we project 20% growth this year due to this technological edge.

    Key Strategic Partnerships:
    We have formalized a new research collaboration with **Stanford's AI Ethics Center** focusing on ensuring our multi-agent decision routing remains unbiased and transparent. A second partnership is underway with **MIT's Secure Systems Group** to refine our **API-driven pipelines**, specifically concerning data validation and integrity across heterogeneous data sources like internal PDFs and external web feeds.

    Next Milestone: **End-to-End Demo Deployment**
    The most critical next step is the deployment of a fully integrated, cloud-hosted end-to-end demonstration. This demo will showcase the system's ability to seamlessly **ingest new PDF data**, build a **FAISS vector store** on the fly, and then answer complex, multi-source queries requiring both RAG and live web searching. This major demonstration is set for **late Q2 (June 2025)**. We are confident this will unlock a new tier of client adoption focused on secure, verifiable AI for knowledge management.
    """
}

# Generate the PDFs
for filename, text in docs.items():
    path = os.path.join("sample_pdfs", filename)
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    margin = 50
    text_x = margin
    text_y_start = height - margin

    # Draw Title
    c.setFont("Helvetica-Bold", 14)
    c.drawString(text_x, text_y_start, filename.replace(".pdf", ""))
    
    # Adjust Y position down for the body text
    body_y_start = text_y_start - 30

    # Draw Body Content using the wrapping function
    c.setFont("Helvetica", 10)
    draw_wrapped_text(c, text, text_x, body_y_start, 10, width - margin)
            
    c.save()

print("\n----------------------------------------------------------------------")
print(" 5 NebulaByte sample PDFs generated successfully in 'sample_pdfs/' folder.")
print("----------------------------------------------------------------------\n")