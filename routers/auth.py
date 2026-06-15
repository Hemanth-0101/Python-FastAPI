from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from datetime import timedelta
import database
from model import LoginRequest, TokenData
from repository import users as user_repo
from jwt_token import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenData,
    status_code=status.HTTP_200_OK,
    summary="Login and get JWT access token",
)
def login(payload: LoginRequest, db: Session = Depends(database.get_db)):
    """
    Authenticate with email + password.
    Returns a **Bearer JWT token** valid for 60 minutes.
    Pass this token in the `Authorization: Bearer <token>` header on protected routes.
    """
    user = user_repo.authenticate(payload.email, payload.password, db)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Get current logged-in user profile",
)
def get_me(
    db: Session = Depends(database.get_db),
    current_user=Depends(lambda: None),  # replaced in main.py via jwt_token
):
    """Returns the profile of the currently authenticated user."""
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
    }
