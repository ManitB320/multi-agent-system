import arxiv

def handle_arxiv_query(query: str):

    results = arxiv.Search(query = query, max_results = 3).results()
    summaries = [f"{r.title} - {r.summary[:200]}..." for r in results]
    
    return " | ".join(summaries)
