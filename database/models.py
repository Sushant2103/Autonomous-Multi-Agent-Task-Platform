from dataclasses import dataclass
from typing import Optional


# =========================================================
# USER MODEL
# =========================================================

@dataclass
class User:

    user_id: Optional[int] = None

    name: str = ""

    email: str = ""

    password: str = ""


# =========================================================
# TASK MODEL
# =========================================================

@dataclass
class Task:

    task_id: Optional[int] = None

    user_id: Optional[int] = None

    user_request: str = ""

    status: str = "pending"


# =========================================================
# TASK STEP MODEL
# =========================================================

@dataclass
class TaskStep:

    step_id: Optional[int] = None

    task_id: Optional[int] = None

    step_number: int = 0

    description: str = ""

    assigned_agent: str = ""

    status: str = "pending"

    result: str = ""


# =========================================================
# AGENT LOG MODEL
# =========================================================

@dataclass
class AgentLog:

    log_id: Optional[int] = None

    task_id: Optional[int] = None

    agent_name: str = ""

    action: str = ""

    result: str = ""


# =========================================================
# TASK RESULT MODEL
# =========================================================

@dataclass
class TaskResult:

    result_id: Optional[int] = None

    task_id: Optional[int] = None

    final_response: str = ""