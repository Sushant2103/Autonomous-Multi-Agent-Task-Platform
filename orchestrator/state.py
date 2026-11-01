from typing import TypedDict, Any
class AgentState(TypedDict, total=False):
    user_request: str
    plan: dict[str, Any]
    results: list[dict[str, Any]]
    final_response: str
    status: str
    error_message: str
    database_task_id: int
