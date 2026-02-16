from app.core.security import verify_password
from app.crud.user import get_user_by_email, create_user
from typing import cast
from fastapi import HTTPException, status

def login(user, db):
    db_user = get_user_by_email(db, user.email)
    if not db_user or not verify_password(user.password, cast(str, db_user.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    return db_user

def register(user, db):
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered, please log in"
        )
    return create_user(db, user)
