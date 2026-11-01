import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.agent_routes import router as agent_router
from backend.routes.auth_routes import router as auth_router
from backend.routes.history_routes import router as history_router
from backend.routes.task_routes import router as task_router

app=FastAPI(title="Autonomous Multi-Agent Task Platform",version="2.0.0",description="Dependency-aware multi-agent task execution API")
origins=[x.strip() for x in os.getenv("CORS_ORIGINS","http://localhost:5173,http://127.0.0.1:5173").split(",") if x.strip()]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=True,allow_methods=["GET","POST","PUT","DELETE"],allow_headers=["Authorization","Content-Type"])
app.include_router(agent_router,prefix="/api/agents")
app.include_router(auth_router,prefix="/api/auth")
app.include_router(history_router,prefix="/api/history")
app.include_router(task_router,prefix="/api")
@app.get("/")
def root(): return {"status":"success","message":"Autonomous Multi-Agent Task Platform API is running","version":"2.0.0"}
@app.get("/health")
def health_check(): return {"status":"ok"}
