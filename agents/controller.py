# Controller Agent - decides which agent(s) to call
# For MVP: simple rule-based routing

def route_query(query: str):
    logs = {"decision": "", "agents_used": []}
    
    if "pdf" in query.lower() or "document" in query.lower():
        logs["decision"] = "Routed to PDF Agent"
        logs["agents_used"].append("PDF RAG Agent")
        return "This is a placeholder response from PDF Agent.", logs
    
    elif "recent paper" in query.lower() or "arxiv" in query.lower():
        logs["decision"] = "Routed to ArXiv Agent"
        logs["agents_used"].append("ArXiv Agent")
        return "This is a placeholder response from ArXiv Agent.", logs
    
    elif "news" in query.lower() or "latest" in query.lower():
        logs["decision"] = "Routed to Web Agent"
        logs["agents_used"].append("Web Search Agent")
        return "This is a placeholder response from Web Agent.", logs
    
    else:
        logs["decision"] = "Default to Web Agent"
        logs["agents_used"].append("Web Search Agent")
        return "Fallback response from Web Agent.", logs
