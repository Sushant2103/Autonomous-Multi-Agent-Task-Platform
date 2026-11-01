from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.auth_service import (
    register_user,
    login_user
)


router = APIRouter()


class SignupRequest(BaseModel):

    name: str
    email: str
    password: str


class LoginRequest(BaseModel):

    email: str
    password: str


@router.post("/signup")
def signup(data: SignupRequest):

    result = register_user(
        data.name,
        data.email,
        data.password
    )

    if result["status"] == "failed":

        raise HTTPException(
            status_code=400,
            detail=result["message"]
        )

    return result


@router.post("/login")
def login(data: LoginRequest):

    result = login_user(
        data.email,
        data.password
    )

    if result["status"] == "failed":

        raise HTTPException(
            status_code=401,
            detail=result["message"]
        )

    return result