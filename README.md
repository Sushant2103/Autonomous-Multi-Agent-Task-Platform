# Autonomous Multi-Agent Task Execution Platform — v2

A general-purpose multi-agent workflow application with a dependency-aware planner, capability-based agent registry, parallel DAG execution, research and analysis agents, guarded tool execution, verification, PostgreSQL/pgvector support, and a React dashboard.

## Quick start (Windows PowerShell)

1. Install Python 3.11, Node.js LTS, Git (optional), and Ollama.
2. Create a virtual environment and install dependencies:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

3. Pull the recommended local model:

```powershell
ollama pull qwen3:4b-instruct-2507-q4_K_M
```

4. Configure PostgreSQL using `database/schema_postgres.sql`, then set `DATABASE_URL` in `.env`. To use the existing MySQL database temporarily, leave `DATABASE_URL` blank and configure the `MYSQL_*` variables.
5. Start the backend from the project root:

```powershell
uvicorn backend.main:app --reload
```

6. In another terminal, start the React app:

```powershell
cd frontend
npm install
npm run dev
```

7. Run automated core tests from the project root:

```powershell
python -m pytest tests -q
```

See `MIGRATION_V2.md` for architecture notes, DB migration steps and safety settings. Never commit `.env`. Keep external execution disabled until tools and approval flows have been reviewed.
