"""Register, login, and "who am I". (Member 1)

Account lockout (Member 2) plugs in through core/hooks.py.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core import hooks
from app.core.database import get_db
from app.core.models import User
from app.modules.users.schemas import RegisterIn, TokenOut, UserOut
from app.modules.users.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    exists = (
        db.query(User)
        .filter(
            or_(
                func.lower(User.username) == data.username.lower(),
                func.lower(User.email) == data.email.lower(),
            )
        )
        .first()
    )
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "That username or email is already registered.")
    user = User(
        username=data.username,
        email=data.email.lower(),
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenOut)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    ident = form.username.strip().lower()
    user = (
        db.query(User)
        .filter(or_(func.lower(User.username) == ident, func.lower(User.email) == ident))
        .first()
    )

    for check in hooks.login_before:  # e.g. "is the account locked?"
        check(user)

    if not verify_password(form.password, user.password_hash if user else None):
        if user:
            for callback in hooks.login_failed:  # e.g. count the failed attempt
                callback(db, user)
        # Same message for "no such user" and "wrong password" on purpose.
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong username or password.")

    for callback in hooks.login_success:  # e.g. reset the failed-attempt counter
        callback(db, user)
    return TokenOut(access_token=create_access_token(user.id), user=user)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
