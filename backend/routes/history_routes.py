import os
from fastapi import APIRouter
router=APIRouter()

@router.get("/{user_id}")
def get_history(user_id:int):
    if os.getenv("DATABASE_URL","").startswith(("postgresql://","postgresql+psycopg://")):
        from sqlalchemy import text
        from database.postgres import get_engine
        with get_engine().connect() as conn:
            rows=conn.execute(text("SELECT id AS task_id,user_request,status,created_at FROM workflows WHERE user_id=:uid ORDER BY created_at DESC"),{"uid":user_id}).mappings().all()
            return {"status":"success","tasks":[dict(x) for x in rows]}
    from database.connection import get_connection
    connection=get_connection()
    if connection is None: return {"status":"failed","message":"Database connection failed"}
    cursor=None
    try:
        cursor=connection.cursor(dictionary=True)
        cursor.execute("SELECT task_id,user_request,status,created_at FROM tasks WHERE user_id=%s ORDER BY created_at DESC",(user_id,))
        return {"status":"success","tasks":cursor.fetchall()}
    finally:
        if cursor: cursor.close()
        connection.close()
