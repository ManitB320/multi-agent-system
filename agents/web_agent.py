from duckduckgo_search import DDGS

def handle_web_query(query: str):

    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results = 3))
    summaries = [r["body"] for r in results]
    return " | ".join(summaries)
