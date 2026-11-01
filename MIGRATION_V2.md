# Version 2 migration notes

This is an additive modernization of the original project. PostgreSQL is supported for workflows, task records, history and user registration/login when `DATABASE_URL` is configured. The original MySQL cursor repository remains as a rollback path when `DATABASE_URL` is blank. Existing MySQL records are not copied automatically; run a verified migration before switching a populated production database.

## Main changes
- Planner: Pydantic-validated DAG with unique IDs, known dependencies and cycle detection.
- Registry/router: agent registration by capabilities and typed task routing.
- Scheduler/graph: LangGraph workflow runs independent ready tasks concurrently with bounded retries.
- Research: retains raw findings and source metadata separately from the LLM summary.
- Data: deterministic safe calculator is separate from LLM analysis.
- Execution: external actions require the execution feature flag, a registered tool, and explicit approval.
- Verification: deterministic evidence checks plus optional LLM review.
- Tools: AST allowlist calculator; API helper requires HTTPS host allowlisting and blocks redirects/private IPs.
- Backend: CORS origins are configurable and restrictive by default.
- Frontend: React + TypeScript Vite app replaces the old frontend; old UI is preserved in `frontend-legacy/`.
- Reports: existing `utils/report_generator.py` retained.

## Local setup (Windows PowerShell)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-v2.txt
Copy-Item .env.example .env
ollama pull qwen3:4b-instruct-2507-q4_K_M
```
Edit `.env` with your own values. Never commit `.env` or share it in ZIP files.

## Run backend
```powershell
uvicorn backend.main:app --reload
```

## Run frontend (new terminal)
```powershell
cd frontend
npm install
npm run dev
```

## Run tests
```powershell
python -m pytest tests -q
```

## Database migration
1. Back up the existing MySQL database.
2. Provision PostgreSQL and enable the `vector` extension.
3. Apply `database/schema_postgres.sql`.
4. Write/run a one-time ETL for existing users, tasks, task steps and logs; hash legacy plaintext passwords during migration; verify row counts and representative records.
5. Change service/repository access to SQLAlchemy PostgreSQL only after verification. The original MySQL code is retained for rollback during this transition.

## Safety
- Keep `EXECUTION_TOOLS_ENABLED=false` until tools have been reviewed and tested.
- Do not expose Ollama port 11434 publicly.
- Set `API_ALLOWED_HOSTS` to exact trusted API hostnames before using `tools.api_tool`.
- Never give the LLM unrestricted shell, Python, filesystem, or arbitrary URL execution.
