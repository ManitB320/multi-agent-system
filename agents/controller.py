import json, os, datetime
from agents import pdf_agent, web_agent, arxiv_agent

LOG_FILE = "logs/trace.json" 

def save_log(entry):

    os.makedirs("logs", exist_ok = True)

    try:
        data = json.load(open(LOG_FILE))
    except:
        data = []

    data.append(entry)
    json.dump(data, open(LOG_FILE, "w"), indent = 2)

def route_query(query: str):

    logs = {"query": query, "decision": "", "agents_used": [], "timestamp": str(datetime.datetime.now())}
    
    if "pdf" in query.lower() or "document" in query.lower():
        logs["decision"] = "Routed to PDF Agent"
        logs["agents_used"].append("PDF RAG Agent")
        response = pdf_agent.handle_pdf_query(query)

    elif "recent paper" in query.lower() or "arxiv" in query.lower():
        logs["decision"] = "Routed to ArXiv Agent"
        logs["agents_used"].append("ArXiv Agent")
        response = arxiv_agent.handle_arxiv_query(query)
    
    elif "news" in query.lower() or "latest" in query.lower():
        logs["decision"] = "Routed to Web Agent"
        logs["agents_used"].append("Web Search Agent")
        response = web_agent.handle_web_query(query)
    
    else:
        logs["decision"] = "Default to Web Agent"
        logs["agents_used"].append("Web Search Agent")
        response = web_agent.handle_web_query(query)

    save_log(logs)
    return response, logs
