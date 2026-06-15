from sqlalchemy.orm import Session
from fastapi import status, HTTPException
import database_models
from model import User, UserUpdate, ChangePassword
from hashing import Hash


def create(user: User, db: Session):
    existing = db.query(database_models.Users).filter(
        database_models.Users.email == user.email
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{user.email}' is already registered",
        )

    user_data = user.model_dump()
    user_data["password"] = Hash.bcrypt(user.password)
    new_user = database_models.Users(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_by_id(id: int, db: Session):
    db_user = db.query(database_models.Users).filter(
        database_models.Users.id == id, database_models.Users.is_active == True
    ).first()
    if db_user:
        return db_user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User with id {id} not found",
    )


def get_by_email(email: str, db: Session):
    db_user = db.query(database_models.Users).filter(
        database_models.Users.email == email
    ).first()
    if db_user:
        return db_user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User with email '{email}' not found",
    )


def get_all(db: Session, skip: int, limit: int):
    return (
        db.query(database_models.Users)
        .filter(database_models.Users.is_active == True)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update(id: int, user_update: UserUpdate, db: Session):
    db_user = db.query(database_models.Users).filter(
        database_models.Users.id == id, database_models.Users.is_active == True
    ).first()
    if not db_user:
        raise HTTPException(status_code=404, detail=f"User with id {id} not found")

    # Check email uniqueness if email is being changed
    if user_update.email and user_update.email != db_user.email:
        existing = db.query(database_models.Users).filter(
            database_models.Users.email == user_update.email
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{user_update.email}' is already taken",
            )

    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def change_password(id: int, payload: ChangePassword, db: Session):
    db_user = db.query(database_models.Users).filter(
        database_models.Users.id == id, database_models.Users.is_active == True
    ).first()
    if not db_user:
        raise HTTPException(status_code=404, detail=f"User with id {id} not found")

    if not Hash.verify(db_user.password, payload.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    db_user.password = Hash.bcrypt(payload.new_password)
    db.commit()
    return {"detail": "Password updated successfully"}


def delete(id: int, db: Session):
    db_user = db.query(database_models.Users).filter(
        database_models.Users.id == id, database_models.Users.is_active == True
    ).first()
    if not db_user:
        raise HTTPException(status_code=404, detail=f"User with id {id} not found")

    # Soft delete user and their products
    db_user.is_active = False
    db.query(database_models.Product).filter(
        database_models.Product.user_id == id
    ).update({"is_active": False})

    db.commit()
    return {"detail": f"User {id} and their products deleted successfully"}


def authenticate(email: str, password: str, db: Session):
    db_user = db.query(database_models.Users).filter(
        database_models.Users.email == email
    ).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )
    if not Hash.verify(db_user.password, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return db_user
