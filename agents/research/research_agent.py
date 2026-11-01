import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from agents.research.research_prompt import SYSTEM_PROMPT
from tools.search_tool import search_web
load_dotenv()

def run_research_agent(task):
    description=task.get("description", "").strip()
    if not description: return {"status":"failed","message":"Research task description is missing","data":"","sources":[],"raw_findings":[]}
    try:
        found=search_web(description,max_results=5) or []
        if not found: return {"status":"failed","message":"No web search results were found","data":"","sources":[],"raw_findings":[]}
        sources=[]; evidence=[]
        for i,item in enumerate(found,1):
            url=item.get("url","")
            source={"source_number":i,"title":item.get("title") or "Untitled","url":url}
            sources.append(source)
            evidence.append({**source,"content":item.get("content", ""),"score":item.get("score")})
        prompt=ChatPromptTemplate.from_messages([("system",SYSTEM_PROMPT),("human","Task: {task}\nUse only this evidence: {evidence}\nSummarize key findings and cite source numbers. Clearly flag gaps.")])
        llm=ChatOllama(model=os.getenv("OLLAMA_MODEL","qwen3:4b-instruct-2507-q4_K_M"),base_url=os.getenv("OLLAMA_BASE_URL","http://localhost:11434"),temperature=0,num_ctx=int(os.getenv("OLLAMA_NUM_CTX","4096")))
        summary=(prompt|llm).invoke({"task":description,"evidence":evidence})
        content=str(summary.content).strip()
        if not content: raise ValueError("Research summary was empty")
        return {"status":"success","task":description,"data":content,"sources":sources,"raw_findings":evidence}
    except Exception as exc:
        return {"status":"failed","message":str(exc),"data":"","sources":[],"raw_findings":[]}
