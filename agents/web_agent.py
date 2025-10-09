import os
from dotenv import load_dotenv
import google.generativeai as genai
from duckduckgo_search import DDGS

# --- New Import for Lazy Loading ---
from rag_state import get_synthesis_model 
# --- End New Import ---

# Load environment. DO NOT configure genai globally here.
load_dotenv()

def handle_web_query(query):
    """Fetch top web results and summarize them using Gemini."""

    # Use the lazy loader for the model
    model = get_synthesis_model()

    results = []
    try:
        # Use DDGS context manager for web search
        with DDGS() as ddgs:
            # TWEAK 1: Increase max_results for higher relevance coverage
            results = list(ddgs.text(
                query,          # Use the exact query for general search
                region = "wt-wt",
                max_results=10,       # Increased from 5 to 10
                safesearch="moderate"
            ))
    except Exception as e:
        return {"summary": f"Web search failed: {e}", "raw_results": []}

    if not results:
        return {"summary": "No relevant web results found.", "raw_results": []}

    # TWEAK 2: Standardize and improve context structure
    combined_snippets = []
    for i, r in enumerate(results):
        title = r.get("title", f"Document {i+1} (Title Missing)")
        url = r.get("href", "URL Missing")
        # Use 'body' (common in DDGS) or fallback to 'description'
        snippet_text = r.get("body", r.get("description", "Snippet not available.")) 
        
        # Structure the context clearly for the LLM
        combined_snippets.append(f"--- DOCUMENT {i+1} ---\nTITLE: {title}\nURL: {url}\nSNIPPET: {snippet_text}")

    combined = "\n\n".join(combined_snippets)

    # TWEAK 3: Simplify and focus the summarization prompt
    summary_prompt = f"""
    Based ONLY on the provided documents, summarize the answer to the user query: "{query}"

    Synthesize the information from the documents into a factual, concise, and coherent English response.

    Documents:
    {combined}
    """

    try:
        # Synchronous Gemini call
        response = model.generate_content(summary_prompt)
        summary = response.text.strip()
    except Exception as e:
        # Fallback summary with error
        summary = combined[:1500] + f"\n\n(Gemini summarization failed: {e})"

    # Return structured dictionary
    return {
        "raw_results": results,
        "summary": summary
    }