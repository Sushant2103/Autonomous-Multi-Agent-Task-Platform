import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from langgraph.graph import StateGraph, END
from orchestrator.state import AgentState
from orchestrator.task_manager import get_ready_tasks, validate_dag
from orchestrator.router import route_task

def _run_one(task, prior_results, user_request):
    attempts=int(task.get("max_retries", 1))+1
    last_error=None
    for attempt in range(attempts):
        try:
            agent, result=route_task(task, prior_results, user_request)
            return {"task_id":task["task_id"],"agent":agent,"result":result,"status":"completed","attempts":attempt+1}
        except Exception as exc:
            last_error=str(exc)
    return {"task_id":task["task_id"],"agent":task.get("assigned_agent"),"result":None,"status":"failed","error":last_error,"attempts":attempts}

def execute_plan_node(state: AgentState):
    plan=state.get("plan", {})
    if hasattr(plan,"model_dump"): plan=plan.model_dump()
    results=list(state.get("results", [])); user_request=state.get("user_request", "")
    try: validate_dag(plan)
    except Exception as exc: return {"status":"failed","error_message":str(exc)}
    completed={r["task_id"] for r in results if r.get("status","completed")=="completed"}
    failed={r["task_id"] for r in results if r.get("status")=="failed"}
    max_workers=max(1,min(int(os.getenv("MAX_PARALLEL_AGENTS","2")),8))
    while len(completed)+len(failed) < len(plan.get("tasks", [])):
        ready=get_ready_tasks(plan, completed, failed_task_ids=failed)
        if not ready:
            remaining=[t["task_id"] for t in plan["tasks"] if t["task_id"] not in completed|failed]
            return {"results":results,"status":"failed","error_message":f"Workflow is blocked; unresolved tasks: {remaining}"}
        # Tasks in this batch have all dependencies satisfied before the batch starts.
        batch_results=[]
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures={pool.submit(_run_one,t,list(results),user_request):t for t in ready}
            for future in as_completed(futures): batch_results.append(future.result())
        results.extend(sorted(batch_results,key=lambda x:x["task_id"]))
        for item in batch_results:
            if item["status"]=="completed": completed.add(item["task_id"])
            else: failed.add(item["task_id"])
        if failed:
            return {"results":results,"status":"failed","error_message":"One or more tasks failed: "+", ".join(str(x) for x in sorted(failed))}
    final=next((x for x in results if x.get("agent")=="response"),None)
    return {"results":results,"final_response":str(final.get("result", "")) if final else "","status":"completed","error_message":""}

def build_graph():
    workflow=StateGraph(AgentState)
    workflow.add_node("execute_dag", execute_plan_node)
    workflow.set_entry_point("execute_dag")
    workflow.add_edge("execute_dag", END)
    return workflow.compile()

# Backwards-compatible entry point name used by service layer.
build_workflow=build_graph
