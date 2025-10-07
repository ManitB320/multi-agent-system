import os, json, datetime
from dotenv import load_dotenv
import google.generativeai as genai
from agents import pdf_agent, web_agent, arxiv_agent
import re

# Load environment and configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = "gemini-2.5-flash"

LOG_FILE = "logs/trace.json"

# ---------- Utilities ----------

def save_log(entry):
    os.makedirs("logs", exist_ok=True)

    # Use try/except for reading to handle missing or corrupt file
    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
        
    data.append(entry)

    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ---------- LLM decision maker ----------

async def llm_decide(query: str):
    """
    Ask Gemini which agent(s) to call.
    Returns dict with 'agents_used' and 'reason'.
    Falls back to rule-based if parsing fails.
    """
    model = genai.GenerativeModel(MODEL_NAME)

    system_prompt = """
    You are a routing controller for a multi-agent AI system. 
    
    Your **PRIMARY DIRECTIVE** is to prioritize internal knowledge retrieval.
    
    Available agents:
    1. PDF_RAG — Use this to summarize or extract information from uploaded internal documents (PDFs, reports, meeting notes, or any company-specific data).
    2. Web_Search — Use this to fetch external, general, or recent online information (news, public product details, generic topics).
    3. Arxiv_Search — Use this specifically for queries about scientific papers, academic research, or topics related to ArXiv.

    Return strict JSON:
    {"agents_used": ["PDF_RAG", "Web_Search"], "reason": "..."}

    **STRICT ROUTING RULES:**
    - **RULE 1 (Internal Priority):** If the query mentions **any** term that suggests internal company knowledge or uploaded documents (e.g., 'PDF', 'report', 'document', 'meeting notes'), you **MUST** include **PDF_RAG** in the agents list. If no answer found then use Web_Search instead.
    - **RULE 2 (External):** Use Web_Search for 'news', 'latest', or common knowledge questions.
    - **RULE 3 (Academic):** Use Arxiv_Search for 'paper', 'research', or 'scientific' questions.
    - Combine agents if necessary.
    """
    try:
        # Note: generate_content is synchronous by default, use generate_content_async if the sdk version supports it
        # For simplicity and robustness, we use the synchronous version here since the function is already awaited in route_query.
        response = await model.generate_content_async([system_prompt, f"User query: {query}"])
        text = response.text.strip()

        # If structured output is used, we might not need the regex search
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # If structured output failed, fall back to regex
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                raise ValueError("No valid JSON found in LLM output.")

        return data
    
    except (genai.errors.APIError, Exception) as e: # Catch API errors too
        # Fallback: rule-based
        agents_used = []
        reason = f"LLM routing failed ({type(e).__name__}: {e}); used rule-based fallback."
        q = query.lower()
        if "pdf" in q or "document" in q:
            agents_used = ["PDF_RAG"]
        elif "arxiv" in q or "paper" in q:
            agents_used = ["Arxiv_Search"]
        else: # Default to Web_Search for everything else, covers news, latest, recent
            agents_used = ["Web_Search"] 
        return {"agents_used": agents_used, "reason": reason}

# ---------- LLM summarizer ----------

async def synthesize_answer(agent_outputs: list):
    """
    Combine multiple agent responses into a single summarized answer.
    Each element of agent_outputs is a dict: {"agent": name, "content": text}
    """
    combined_text = "\n\n".join(
        [f"From {a['agent']}:\n{a['content']}" for a in agent_outputs]
    )

    prompt = f"""
    You are an expert AI orchestrator. Your task is to perform a detailed, multi-source synthesis.
    Synthesize and merge ALL the factual information provided below into ONE cohesive, concise final answer.

    **CONSTRAINTS:**
    1. Do not begin with phrases like 'Based on the agent outputs,' or 'Here is a summary.' Just provide the direct answer.
    2. If two sources provide conflicting information, note the conflict (e.g., 'Source A says X, but Source B suggests Y').
    3. Preserve key technical details, names, and numbers.
    4. **Final Answer Structure:** Use bullet points or numbered lists if the answer is complex, otherwise, a single paragraph is fine.

    Agent Outputs to Synthesize:
    {combined_text}
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        # FIX 1: MUST await the async API call
        response = await model.generate_content_async(prompt)
        return response.text.strip()
    except Exception as e:
        return f"(Summarization failed: {e})\n\n" + combined_text

# ---------- Main routing orchestrator ----------

async def route_query(query: str):
    log_entry = {
        "timestamp": str(datetime.datetime.now()),
        "query": query,
        "decision": "",
        "agents_used": [],
        "reason": "",
        "retrieved_docs": [],
        "final_answer": ""
    }

    decision = await llm_decide(query)
    agents_used = decision.get("agents_used", [])
    log_entry["decision"] = "LLM decision"
    log_entry["agents_used"] = agents_used
    log_entry["reason"] = decision.get("reason", "")

    agent_outputs = []

    for agent in agents_used:
        # NOTE: Agent calls are synchronous, so they are NOT awaited
        if agent == "PDF_RAG":
            result = pdf_agent.handle_pdf_query(query)
            # PDF_RAG now returns a dict
            if isinstance(result, dict) and "summary" in result:
                resp = result["summary"]
                # Log raw chunks from the PDF agent
                log_entry["retrieved_docs"].append({"PDF_RAG_Raw": "\n\n".join(result.get("raw_results", []))})
            else:
                resp = str(result)

        elif agent == "Web_Search":
            result = web_agent.handle_web_query(query)
            if isinstance(result, dict) and "summary" in result:
                resp = result["summary"]
                # Log raw search bodies
                log_entry["retrieved_docs"].append({"Web_Search_Raw": "\n\n".join([r.get("body", "N/A") for r in result.get("raw_results", [])])})
            else:
                resp = str(result)

        elif agent == "Arxiv_Search":
            result = arxiv_agent.handle_arxiv_query(query)
            if isinstance(result, dict) and "summary" in result:
                resp = result["summary"]
                # Log Arxiv titles
                log_entry["retrieved_docs"].append({"Arxiv_Search_Titles": "\n\n".join([f"Title: {r['title']}" for r in result.get("papers", [])])})
            else:
                resp = str(result)
        else:
            continue
            
        agent_outputs.append({"agent": agent, "content": resp})
        log_entry["retrieved_docs"].append({agent: resp[:500]}) # sample snippet

    # Synthesize if multiple agents used
    if len(agent_outputs) > 1:
        # FIX 2: MUST await the async synthesize_answer function
        final_answer = await synthesize_answer(agent_outputs)
    else:
        final_answer = agent_outputs[0]["content"] if agent_outputs else "(No response)"

    log_entry["final_answer"] = final_answer
    save_log(log_entry)
    return final_answer, log_entry