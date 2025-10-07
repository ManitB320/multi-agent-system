import os
from dotenv import load_dotenv
from google import genai
from arxiv import Search, SortCriterion

# Load environment and configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def handle_arxiv_query(query):
    """Search ArXiv and summarize top abstracts with Gemini."""
    
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