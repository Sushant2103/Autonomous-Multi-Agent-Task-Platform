from typing import Any, Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator

AgentName = Literal["research_agent", "data_agent", "execution_agent", "verification_agent", "response_agent"]

class Task(BaseModel):
    model_config = ConfigDict(extra="forbid")
    task_id: int = Field(ge=1)
    description: str = Field(min_length=3, max_length=4000)
    assigned_agent: AgentName
    priority: int = Field(default=3, ge=1, le=5, description="1 is highest priority")
    depends_on: list[int] = Field(default_factory=list)
    required_capabilities: list[str] = Field(default_factory=list)
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None
    calculation_expression: str | None = Field(default=None, max_length=200)
    timeout_seconds: int = Field(default=120, ge=1, le=1800)
    max_retries: int = Field(default=1, ge=0, le=3)

class Plan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    goal: str = Field(min_length=1, max_length=4000)
    tasks: list[Task] = Field(min_length=1, max_length=40)

    @model_validator(mode="after")
    def validate_dag(self):
        ids=[t.task_id for t in self.tasks]
        if len(ids) != len(set(ids)):
            raise ValueError("Task IDs must be unique")
        by_id={t.task_id:t for t in self.tasks}
        responses=[t for t in self.tasks if t.assigned_agent == "response_agent"]
        if len(responses) != 1:
            raise ValueError("A plan must contain exactly one response_agent task")
        final=responses[0]
        if final.task_id != self.tasks[-1].task_id:
            raise ValueError("The response_agent task must be last")
        for task in self.tasks:
            if task.task_id in task.depends_on:
                raise ValueError(f"Task {task.task_id} cannot depend on itself")
            if len(task.depends_on) != len(set(task.depends_on)):
                raise ValueError(f"Task {task.task_id} has duplicate dependencies")
            unknown=set(task.depends_on)-set(by_id)
            if unknown:
                raise ValueError(f"Task {task.task_id} has unknown dependencies: {sorted(unknown)}")
        # Kahn topological check: order in the JSON is not required to be topological.
        remaining={tid:set(t.depends_on) for tid,t in by_id.items()}
        ready=[tid for tid,deps in remaining.items() if not deps]
        visited=[]
        while ready:
            current=ready.pop()
            visited.append(current)
            for tid,deps in remaining.items():
                if current in deps:
                    deps.remove(current)
                    if not deps and tid not in visited and tid not in ready:
                        ready.append(tid)
        if len(visited) != len(by_id):
            raise ValueError("Task dependencies contain a cycle")
        all_other_ids=set(ids)-{final.task_id}
        if set(final.depends_on) != all_other_ids:
            raise ValueError("Final response task must depend on every other task")
        return self
