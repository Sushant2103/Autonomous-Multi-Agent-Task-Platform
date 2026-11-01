import os
from dotenv import load_dotenv
from agents.registry import registry
from agents.research.research_agent import run_research_agent
from agents.data.data_agent import run_data_agent
from agents.execution.execution_agent import run_execution_agent
from agents.verification.verification_agent import run_verification_agent
from agents.response.response_agent import run_response_agent

load_dotenv()

def _register_defaults():
    if registry.describe(): return
    registry.register("research_agent", {"research", "web_search", "evidence"}, run_research_agent)
    registry.register("data_agent", {"analysis", "data", "calculation"}, run_data_agent)
    registry.register("execution_agent", {"tool_execution", "external_action"}, run_execution_agent)
    registry.register("verification_agent", {"verification", "quality_check"}, run_verification_agent)
    registry.register("response_agent", {"synthesis", "final_response"}, run_response_agent)
_register_defaults()

def combine_previous_results(results):
    return "\n\n".join(f"Task {x.get('task_id')} ({x.get('agent')}):\n{x.get('result')}" for x in (results or [])) or "No previous results."

def route_task(task, results=None, user_request=""):
    results=results or []
    agent_name=task.get("assigned_agent", "")
    required=task.get("required_capabilities", [])
    if agent_name:
        spec=registry.get(agent_name)
        # Prefer the planner's assignment when it satisfies the requested capabilities;
        # otherwise resolve the task dynamically from the capability registry.
        if required and not set(required).issubset(spec.capabilities):
            spec=registry.select(required)
            agent_name=spec.name
    else:
        spec=registry.select(required)
        agent_name=spec.name
    context=dict(task)
    context["previous_results"]=results
    context["user_request"]=user_request
    if agent_name == "verification_agent":
        context["previous_result"]=combine_previous_results(results)
        output=spec.runner(context, context["previous_result"])
    elif agent_name == "response_agent":
        output=spec.runner(user_request, results)
    else:
        output=spec.runner(context)
    if isinstance(output, dict) and output.get("status") == "failed":
        raise RuntimeError(output.get("message", f"{agent_name} failed"))
    return agent_name.removesuffix("_agent"), output
