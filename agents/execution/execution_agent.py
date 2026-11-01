import os
from tools.gateway import execute_registered_tool

def run_execution_agent(task):
    if os.getenv("EXECUTION_TOOLS_ENABLED","false").lower() != "true":
        return {"status":"success","execution_status":"not_executed","message":"Execution is disabled. No external action was performed."}
    tool_name=task.get("tool_name")
    tool_args=task.get("tool_args",{})
    authorized=bool(task.get("user_approved",False))
    if not tool_name:
        return {"status":"success","execution_status":"not_executed","message":"No registered tool was specified; no action was performed."}
    try:
        result=execute_registered_tool(tool_name,tool_args,authorized=authorized)
        return {"status":"success","execution_status":"executed","tool":tool_name,"result":result}
    except Exception as exc:
        return {"status":"failed","execution_status":"failed","message":str(exc)}
