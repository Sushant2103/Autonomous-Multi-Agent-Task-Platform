import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from tools.calculator_tool import calculate
load_dotenv()

def format_previous_results(previous_results):
    return "\n\n".join(f"Task ID: {x.get('task_id')}\nAgent: {x.get('agent')}\nResult: {x.get('result')}" for x in (previous_results or [])) or "No previous results are available."

def run_data_agent(task):
    description=task.get("description", "")
    if not description.strip(): return {"status":"failed","message":"Task description is empty"}
    # Deterministic calculation is exposed as a separate tool; never eval model/user code.
    expression=task.get("calculation_expression")
    calculation_result=calculate(expression) if expression else None
    try:
        llm=ChatOllama(model=os.getenv("OLLAMA_MODEL","qwen3:4b-instruct-2507-q4_K_M"),base_url=os.getenv("OLLAMA_BASE_URL","http://localhost:11434"),temperature=0,num_ctx=int(os.getenv("OLLAMA_NUM_CTX","4096")))
        prompt=f"TASK:\n{description}\n\nPRIOR RESULTS:\n{format_previous_results(task.get('previous_results'))}\n\nDETERMINISTIC CALCULATION (if supplied):\n{calculation_result}\n\nAnalyze only available evidence. Do not invent data. Clearly label assumptions and missing inputs."
        response=llm.invoke([SystemMessage(content="You are a careful data analyst. Use deterministic results as authoritative; do not fabricate numbers."),HumanMessage(content=prompt)])
        content=str(response.content).strip()
        if not content: raise ValueError("Data model returned an empty response")
        return {"status":"success","task":description,"data":content,"calculation":calculation_result,"previous_results_used":len(task.get("previous_results",[]))}
    except Exception as exc:
        if calculation_result and calculation_result.get("status")=="success":
            return {"status":"success","task":description,"data":f"Deterministic calculation result: {calculation_result['result']}","calculation":calculation_result,"llm_analysis_unavailable":str(exc)}
        return {"status":"failed","message":f"Data analysis failed: {exc}","task":description}
