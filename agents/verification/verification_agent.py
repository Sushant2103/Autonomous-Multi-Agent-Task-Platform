import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
load_dotenv()

def run_verification_agent(task, result=None):
    description=task.get("description", "") if isinstance(task,dict) else str(task)
    evidence=result if result is not None else task.get("previous_result", "") if isinstance(task,dict) else ""
    # Deterministic gates before optional LLM review.
    if evidence is None or not str(evidence).strip():
        return {"status":"failed","verified":False,"checks":["non_empty_result"],"message":"No result was supplied for verification"}
    issues=[]
    if isinstance(evidence,dict):
        if evidence.get("status")=="failed": issues.append("upstream_result_marked_failed")
        for src in evidence.get("sources",[]):
            if not src.get("url","").startswith(("http://","https://")): issues.append("source_missing_valid_http_url")
    deterministic={"non_empty_result":True,"upstream_status_ok":not issues,"issues":sorted(set(issues))}
    try:
        llm=ChatOllama(model=os.getenv("OLLAMA_MODEL","qwen3:4b-instruct-2507-q4_K_M"),base_url=os.getenv("OLLAMA_BASE_URL","http://localhost:11434"),temperature=0,num_ctx=int(os.getenv("OLLAMA_NUM_CTX","4096")))
        prompt=f"Review this task and result for completeness, contradictions, unsupported claims and missing evidence. Do not claim external verification. Return concise findings.\nTASK: {description}\nRESULT: {evidence}"
        review=str(llm.invoke(prompt).content).strip()
        return {"status":"success" if not issues else "failed","verified":not issues,"checks":deterministic,"review":review,"message":"Verification review completed"}
    except Exception as exc:
        return {"status":"success" if not issues else "failed","verified":not issues,"checks":deterministic,"review":"LLM review unavailable","warning":str(exc)}
