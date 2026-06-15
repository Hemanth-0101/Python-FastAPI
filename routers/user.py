from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List
import database
from model import User, UserUpdate, showUser, ChangePassword
from repository import users
from jwt_token import get_current_user
import database_models

router = APIRouter(prefix="/user", tags=["Users"])


# ── READ ──────────────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=List[showUser],
    status_code=status.HTTP_200_OK,
    summary="List all active users (requires auth)",
)
def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(database.get_db),
    current_user: database_models.Users = Depends(get_current_user),
):
    return users.get_all(db, skip, limit)


@router.get(
    "/{id}",
    response_model=showUser,
    status_code=status.HTTP_200_OK,
    summary="Get a user by ID (with their products)",
)
def get_user(id: int, db: Session = Depends(database.get_db)):
    return users.get_by_id(id, db)


# ── CREATE ────────────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=showUser,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def create_user(u: User, db: Session = Depends(database.get_db)):
    return users.create(u, db)


# ── UPDATE ────────────────────────────────────────────────────────────────────

@router.put(
    "/{id}",
    response_model=showUser,
    status_code=status.HTTP_200_OK,
    summary="Update user name or email (requires auth)",
)
def update_user(
    id: int,
    user_update: UserUpdate,
    db: Session = Depends(database.get_db),
    current_user: database_models.Users = Depends(get_current_user),
):
    return users.update(id, user_update, db)


@router.patch(
    "/{id}/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change user password (requires auth)",
)
def change_password(
    id: int,
    payload: ChangePassword,
    db: Session = Depends(database.get_db),
    current_user: database_models.Users = Depends(get_current_user),
):
    return users.change_password(id, payload, db)


# ── DELETE ────────────────────────────────────────────────────────────────────

@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Soft-delete a user and their products (requires auth)",
)
def delete_user(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: database_models.Users = Depends(get_current_user),
):
    return users.delete(id, db)
