from collections import defaultdict, deque

def _tasks(plan):
    if hasattr(plan, "model_dump"): plan=plan.model_dump()
    tasks=plan.get("tasks", [])
    if not isinstance(tasks, list): raise ValueError("Invalid plan: tasks must be a list")
    ids=[t.get("task_id") for t in tasks]
    if any(x is None for x in ids) or len(ids)!=len(set(ids)): raise ValueError("Task IDs must exist and be unique")
    known=set(ids)
    for task in tasks:
        deps=task.get("depends_on", [])
        if not isinstance(deps,list) or len(deps)!=len(set(deps)): raise ValueError(f"Invalid dependencies for task {task['task_id']}")
        missing=set(deps)-known
        if missing: raise ValueError(f"Task {task['task_id']} references unknown dependencies {sorted(missing)}")
        if task['task_id'] in deps: raise ValueError(f"Task {task['task_id']} depends on itself")
    return tasks

def validate_dag(plan):
    tasks=_tasks(plan); deps={t['task_id']:set(t.get('depends_on',[])) for t in tasks}
    ready=deque(k for k,v in deps.items() if not v); visited=0
    while ready:
        node=ready.popleft(); visited+=1
        for child,parents in deps.items():
            if node in parents:
                parents.remove(node)
                if not parents: ready.append(child)
    if visited != len(tasks): raise ValueError("Task graph contains a dependency cycle")
    return True

def get_ready_tasks(plan, completed_task_ids, running_task_ids=None, failed_task_ids=None):
    tasks=_tasks(plan); validate_dag(plan)
    completed=set(completed_task_ids); running=set(running_task_ids or []); failed=set(failed_task_ids or [])
    ready=[t for t in tasks if t['task_id'] not in completed|running|failed and set(t.get('depends_on',[])).issubset(completed)]
    return sorted(ready, key=lambda t:(t.get('priority',3), t['task_id']))

def get_next_task(plan, completed_task_ids):
    ready=get_ready_tasks(plan, completed_task_ids)
    return ready[0] if ready else None
