import pytest
from agents.planner.schemas import Plan
from orchestrator.task_manager import get_ready_tasks, validate_dag
from tools.calculator_tool import calculate
from tools.gateway import ToolRegistry

def plan(tasks): return Plan.model_validate({"goal":"test","tasks":tasks})
def task(i,agent="data_agent",deps=None): return {"task_id":i,"description":f"Do task {i}","assigned_agent":agent,"priority":2,"depends_on":deps or []}
def test_valid_dag_and_ready_tasks():
    p=plan([task(1),task(2),task(3,"response_agent",[1,2])])
    assert validate_dag(p)
    assert {x['task_id'] for x in get_ready_tasks(p,[])}=={1,2}
    assert [x['task_id'] for x in get_ready_tasks(p,[1,2])]==[3]
def test_cycle_rejected():
    with pytest.raises(ValueError): plan([task(1,"data_agent",[2]),task(2,"data_agent",[1]),task(3,"response_agent",[1,2])])
def test_unknown_dependency_rejected():
    with pytest.raises(ValueError): plan([task(1,"data_agent",[99]),task(2,"response_agent",[1])])
def test_final_response_must_depend_on_all():
    with pytest.raises(ValueError): plan([task(1),task(2,"response_agent",[])])
def test_safe_calculator():
    assert calculate("(25/100)*800")["result"]==200
    assert calculate("__import__('os').system('whoami')")["status"]=="failed"
def test_tool_requires_approval():
    r=ToolRegistry(); r.register("danger",lambda: "done",requires_approval=True)
    with pytest.raises(PermissionError): r.execute("danger",{},authorized=False)
    assert r.execute("danger",{},authorized=True)=="done"


def test_capability_registry_selects_agent():
    from agents.registry import AgentRegistry
    registry=AgentRegistry()
    registry.register("research",{"web_search","evidence"},lambda x:x)
    registry.register("analyst",{"analysis","calculation"},lambda x:x)
    assert registry.select(["calculation"]).name=="analyst"
