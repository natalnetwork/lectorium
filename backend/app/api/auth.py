from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app import database
from backend.app.models.db_models import UserRow
from backend.app.services import auth as auth_service

router = APIRouter(prefix="/auth")


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


@router.post("/register", response_model=TokenResponse)
def register(body: RegisterRequest) -> TokenResponse:
    with Session(database.engine) as session:
        existing = session.query(UserRow).filter_by(username=body.username).first()
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )
        user_id = str(uuid.uuid4())
        session.add(
            UserRow(
                id=user_id,
                username=body.username,
                hashed_password=auth_service.hash_password(body.password),
            )
        )
        session.commit()

    return TokenResponse(
        access_token=auth_service.create_token(user_id),
        username=body.username,
    )


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest) -> TokenResponse:
    with Session(database.engine) as session:
        user = session.query(UserRow).filter_by(username=body.username).first()
        if user is None or not auth_service.verify_password(body.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        user_id = user.id
        username = user.username

    return TokenResponse(
        access_token=auth_service.create_token(user_id),
        username=username,
    )
