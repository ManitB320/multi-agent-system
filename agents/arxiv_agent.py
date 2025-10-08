import os
from dotenv import load_dotenv
import google.generativeai as genai
from arxiv import Search, SortCriterion

# --- New Import for Lazy Loading ---
from rag_state import get_synthesis_model 
# --- End New Import ---

# Load environment. DO NOT configure genai globally here.
load_dotenv()

def handle_arxiv_query(query):
    """Search ArXiv and summarize top abstracts with Gemini."""
    
    # Use the lazy loader for the model
    model = get_synthesis_model() # <--- LAZY LOAD CALL
    
    # Search for up to 5 papers, sorting by most recent update
    search = Search(
        query=query, 
        max_results=5, 
        sort_by=SortCriterion.SubmittedDate # Sort by submission date for relevance
    )

    results = []
    try:
        # Collect results and format them
        for r in search.results():
            results.append({
                "title": r.title,
                "summary": r.summary,
                "url": r.entry_id,
                "published": str(r.published)
            })
    except Exception as e:
        return {"summary": f"ArXiv search failed: {e}", "papers": []}

    if not results:
        return {"summary": "No relevant papers found on ArXiv.", "papers": []}

    # Prepare context for the LLM
    combined = "\n\n---\n\n".join(
        [f"Title: {r['title']}\nAbstract: {r['summary']}" for r in results]
    )

    prompt = f"""
    You are a research summarization model. Summarize the following research papers into a concise, factual, plain-English answer that directly addresses the user's question:
    "{query}"

    Only mention key insights or recent findings.

    Papers Context:
    ---
    {combined}
    ---
    """

    try:
        # Synchronous Gemini call
        response = model.generate_content(prompt)
        summary = response.text.strip()
    except Exception as e:
        # Fallback summary with error
        summary = combined[:1000] + f"\n\n(Gemini summarization failed: {e})"

    # Return structured dictionary
    return {
        "papers": results,
        "summary": summary
    }