import os
from sqlalchemy import text
from database.postgres import get_engine

def create_workflow(user_id, user_request):
    with get_engine().begin() as conn:
        row=conn.execute(text("INSERT INTO workflows (user_id,user_request,status) VALUES (:uid,:request,'running') RETURNING id"),{"uid":user_id,"request":user_request}).first()
        return int(row[0])

def save_plan(workflow_id, plan):
    with get_engine().begin() as conn:
        conn.execute(text("UPDATE workflows SET plan=CAST(:plan AS jsonb) WHERE id=:id"),{"id":workflow_id,"plan":__import__('json').dumps(plan)})
        for task in plan.get("tasks",[]):
            conn.execute(text("INSERT INTO workflow_tasks (workflow_id,task_id,agent,status,dependencies) VALUES (:wid,:tid,:agent,'pending',CAST(:deps AS jsonb)) ON CONFLICT (workflow_id,task_id) DO UPDATE SET agent=EXCLUDED.agent,dependencies=EXCLUDED.dependencies"),{"wid":workflow_id,"tid":task["task_id"],"agent":task["assigned_agent"],"deps":__import__('json').dumps(task.get("depends_on",[]))})

def save_results(workflow_id, results):
    import json
    with get_engine().begin() as conn:
        for item in results:
            conn.execute(text("UPDATE workflow_tasks SET status=:status,result=CAST(:result AS jsonb) WHERE workflow_id=:wid AND task_id=:tid"),{"status":item.get("status","completed"),"result":json.dumps(item.get("result"),default=str),"wid":workflow_id,"tid":item["task_id"]})

def update_workflow_status(workflow_id,status):
    with get_engine().begin() as conn: conn.execute(text("UPDATE workflows SET status=:status WHERE id=:id"),{"status":status,"id":workflow_id})

def get_workflow(workflow_id):
    with get_engine().connect() as conn:
        row=conn.execute(text("SELECT id,user_request,status,plan,created_at FROM workflows WHERE id=:id"),{"id":workflow_id}).mappings().first()
        if not row: return None
        tasks=conn.execute(text("SELECT task_id,agent,status,dependencies,result FROM workflow_tasks WHERE workflow_id=:id ORDER BY task_id"),{"id":workflow_id}).mappings().all()
        return {"workflow":dict(row),"tasks":[dict(x) for x in tasks]}
