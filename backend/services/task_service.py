import os

def execute_task(user_id, user_request):
    from agents.planner.planner_agent import create_plan
    from orchestrator.graph import build_graph
    from utils.report_generator import generate_pdf_report

    use_postgres=os.getenv("DATABASE_URL", "").startswith(("postgresql://", "postgresql+psycopg://"))
    workflow_id=None
    try:
        if use_postgres:
            from database.postgres_repository import create_workflow, save_plan, save_results, update_workflow_status
            workflow_id=create_workflow(user_id,user_request)
        else:
            from database.task_repository import create_task, save_task_result, update_task_status
            workflow_id=create_task(user_id,user_request)
            if workflow_id is None: return {"status":"failed","message":"Could not create task in MySQL. Configure DATABASE_URL for PostgreSQL or check MySQL settings."}

        plan=create_plan(user_request)
        plan_data=plan.model_dump()
        if use_postgres: save_plan(workflow_id,plan_data)
        graph=build_graph()
        final_state=graph.invoke({"user_request":user_request,"plan":plan_data,"results":[],"status":"starting"})
        results=final_state.get("results",[])
        if final_state.get("status") != "completed":
            if use_postgres: update_workflow_status(workflow_id,"failed"); save_results(workflow_id,results)
            else: update_task_status(workflow_id,"failed")
            return {"status":"failed","message":final_state.get("error_message","Workflow did not complete"),"task_id":workflow_id,"plan":plan_data,"results":results}
        final_response=final_state.get("final_response", "")
        if not final_response:
            if use_postgres: update_workflow_status(workflow_id,"failed"); save_results(workflow_id,results)
            else: update_task_status(workflow_id,"failed")
            return {"status":"failed","message":"Response Agent did not generate a final response.","task_id":workflow_id}
        if use_postgres:
            save_results(workflow_id,results); update_workflow_status(workflow_id,"completed")
        else:
            save_task_result(workflow_id,final_response); update_task_status(workflow_id,"completed")
        pdf_path=None
        try: pdf_path=generate_pdf_report(user_request,plan,results)
        except Exception as exc: print("PDF generation failed:",exc)
        return {"status":"success","task_id":workflow_id,"user_request":user_request,"plan":plan_data,"results":results,"final_response":final_response,"pdf_report":pdf_path}
    except Exception as exc:
        if workflow_id is not None:
            try:
                if use_postgres:
                    from database.postgres_repository import update_workflow_status
                    update_workflow_status(workflow_id,"failed")
                else:
                    from database.task_repository import update_task_status
                    update_task_status(workflow_id,"failed")
            except Exception: pass
        return {"status":"failed","message":str(exc),"task_id":workflow_id}


def get_task_details(task_id):
    if os.getenv("DATABASE_URL", "").startswith(("postgresql://", "postgresql+psycopg://")):
        from database.postgres_repository import get_workflow
        result=get_workflow(task_id)
        return {"status":"success","data":result} if result else {"status":"failed","message":"Workflow not found"}
    from database.connection import get_connection
    connection=get_connection()
    if connection is None: return {"status":"failed","message":"MySQL connection failed"}
    cursor=None
    try:
        cursor=connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tasks WHERE task_id = %s",(task_id,)); task=cursor.fetchone()
        if not task: return {"status":"failed","message":"Task not found"}
        cursor.execute("SELECT * FROM task_steps WHERE task_id = %s ORDER BY step_number",(task_id,)); steps=cursor.fetchall()
        cursor.execute("SELECT * FROM agent_logs WHERE task_id = %s ORDER BY created_at",(task_id,)); logs=cursor.fetchall()
        cursor.execute("SELECT * FROM task_results WHERE task_id = %s ORDER BY created_at DESC LIMIT 1",(task_id,)); final_result=cursor.fetchone()
        return {"status":"success","task":task,"steps":steps,"agent_logs":logs,"final_result":final_result}
    except Exception as exc: return {"status":"failed","message":str(exc)}
    finally:
        if cursor: cursor.close()
        connection.close()
