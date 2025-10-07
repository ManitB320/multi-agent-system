import os
from dotenv import load_dotenv
import google.generativeai as genai
from duckduckgo_search import DDGS

# Load environment and configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash") 

def handle_web_query(query):
    """Fetch top web results and summarize them using Gemini."""

    results = []
    try:
        # Use DDGS context manager for web search
        with DDGS() as ddgs:
            # We explicitly convert the generator to a list here to ensure we have all results
            results = list(ddgs.text(
                f"{query}",
                max_results=5,
                safesearch="moderate"
            ))
    except Exception as e:
        return {"summary": f"Web search failed: {e}", "raw_results": []}

    if not results:
        return {"summary": "No relevant web results found.", "raw_results": []}

    # Prepare context for the LLM (using the 'body' snippet)
    combined = "\n\n---\n\n".join([r.get("body", "") for r in results[:5]])

    # Gemini summarization prompt
    summary_prompt = f"""
    You are a factual summarization assistant. Summarize the following search result snippets into a concise English answer for the user query: "{query}"

    Focus on the most recent and relevant facts only, and use the snippets provided.

    Web snippets:
    ---
    {combined}
    ---
    """

    try:
        # Synchronous Gemini call
        response = model.generate_content(summary_prompt)
        summary = response.text.strip()
    except Exception as e:
        # Fallback summary with error
        summary = combined[:1000] + f"\n\n(Gemini summarization failed: {e})"

    # Return structured dictionary
    return {
        "raw_results": results[:5],
        "summary": summary
    }