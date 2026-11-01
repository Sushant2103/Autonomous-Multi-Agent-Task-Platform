from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


router = APIRouter()


class TaskRequest(BaseModel):

    user_id: int
    user_request: str


@router.post("/execute")
def create_and_execute_task(
    data: TaskRequest
):

    from backend.services.task_service import execute_task

    if not data.user_request.strip():

        raise HTTPException(
            status_code=400,
            detail="Task request cannot be empty."
        )

    result = execute_task(
        data.user_id,
        data.user_request
    )

    if result["status"] == "failed":

        raise HTTPException(
            status_code=500,
            detail=result["message"]
        )

    return result


@router.get("/{task_id}")
def get_task(task_id: int):

    from backend.services.task_service import get_task_details

    result = get_task_details(
        task_id
    )

    if result["status"] == "failed":

        raise HTTPException(
            status_code=404,
            detail=result["message"]
        )

    return result