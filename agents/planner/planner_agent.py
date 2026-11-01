
import json
import os
from copy import deepcopy

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from agents.planner.schemas import Plan
from agents.planner.planner_prompt import SYSTEM_PROMPT

load_dotenv()


def _model():
    return ChatOllama(
        model=os.getenv(
            "OLLAMA_MODEL",
            "qwen3:4b-instruct-2507-q4_K_M"
        ),
        base_url=os.getenv(
            "OLLAMA_BASE_URL",
            "http://localhost:11434"
        ),
        temperature=0,
        num_ctx=int(os.getenv("OLLAMA_NUM_CTX", "4096")),
        format="json",
    )


def extract_json(raw_response):
    if hasattr(raw_response, "content"):
        raw_response = raw_response.content

    if not isinstance(raw_response, str):
        raise ValueError("Planner response must be text")

    cleaned = raw_response.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start < 0 or end < start:
        raise ValueError("Planner did not return a JSON object")

    return json.loads(cleaned[start:end + 1])


def normalize_plan(data):
    """Normalize model-generated IDs, priorities, and dependencies."""
    data = deepcopy(data)

    if not isinstance(data, dict):
        raise ValueError("Planner response must be a JSON object")

    tasks = data.get("tasks")

    if not isinstance(tasks, list) or not tasks:
        raise ValueError("Planner returned no tasks")

    if len(tasks) > 40:
        raise ValueError("Planner returned more than 40 tasks")

    if not all(isinstance(task, dict) for task in tasks):
        raise ValueError("Planner returned an invalid task")

    response_tasks = [
        task for task in tasks
        if task.get("assigned_agent") == "response_agent"
    ]

    if len(response_tasks) != 1:
        raise ValueError(
            "Planner must create exactly one response_agent task"
        )

    # Keep the final response task at the end.
    final_task = response_tasks[0]
    other_tasks = [task for task in tasks if task is not final_task]
    ordered_tasks = other_tasks + [final_task]

    # Build an old-ID mapping when IDs are unique.
    old_ids = [task.get("task_id") for task in ordered_tasks]

    ids_are_unique = (
        all(
            isinstance(value, int) and not isinstance(value, bool)
            for value in old_ids
        )
        and len(set(old_ids)) == len(old_ids)
    )

    id_map = {}

    if ids_are_unique:
        id_map = {
            old_id: index
            for index, old_id in enumerate(old_ids, start=1)
        }

    for index, task in enumerate(ordered_tasks, start=1):
        # Normalize task IDs.
        task["task_id"] = index

        # Normalize priorities to the allowed range of 1–5.
        priority = task.get("priority", 3)

        if not isinstance(priority, int) or isinstance(priority, bool):
            priority = 3

        task["priority"] = max(1, min(5, priority))

        # Normalize dependencies.
        if index == len(ordered_tasks):
            # Final response depends on every preceding task.
            task["depends_on"] = list(range(1, index))

        elif ids_are_unique:
            old_dependencies = task.get("depends_on", [])

            if not isinstance(old_dependencies, list):
                old_dependencies = []

            task["depends_on"] = [
                id_map[dep]
                for dep in old_dependencies
                if (
                    isinstance(dep, int)
                    and not isinstance(dep, bool)
                    and dep in id_map
                    and id_map[dep] != index
                )
            ]

        else:
            # Fallback to a sequential dependency chain.
            task["depends_on"] = [index - 1] if index > 1 else []

    data["tasks"] = ordered_tasks
    return data


def create_plan(user_request: str) -> Plan:
    if not user_request or not user_request.strip():
        raise ValueError("User request cannot be empty")

    prompt = (
        SYSTEM_PROMPT
        + "\n\nUSER REQUEST:\n"
        + user_request.strip()
        + "\n\nReturn only JSON matching the Plan schema."
    )

    response = _model().invoke(prompt)
    raw_plan = extract_json(response)
    normalized_plan = normalize_plan(raw_plan)

    return Plan.model_validate(normalized_plan)


def run_planner_agent(user_request: str):
    return create_plan(user_request)
