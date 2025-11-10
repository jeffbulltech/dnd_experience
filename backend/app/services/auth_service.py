from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import User
from ..schemas.auth import LoginRequest, TokenResponse, UserCreate, UserRead

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def create_user(db: Session, payload: UserCreate) -> UserRead:
    if db.query(User).filter((User.email == payload.email) | (User.username == payload.username)).first():
        raise ValueError("User with provided email or username already exists.")

    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=pwd_context.hash(payload.password),
        display_name=payload.display_name,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user, from_attributes=True)


def authenticate_user(db: Session, credentials: LoginRequest) -> TokenResponse:
    user = db.query(User).filter(User.username == credentials.username).first()
    if user is None or not pwd_context.verify(credentials.password, user.hashed_password):
        raise ValueError("Invalid username or password.")

    token_expires = datetime.utcnow() + timedelta(hours=6)
    token = jwt.encode(
        {"sub": str(user.id), "exp": token_expires},
        settings.secret_key,
        algorithm=ALGORITHM,
    )
    return TokenResponse(access_token=token)


def get_current_user(db: Session, token: str) -> User:
    try:
        payload: dict[str, Any] = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:  # pragma: no cover
        raise ValueError("Invalid authentication token.") from exc

    user = db.get(User, user_id)
    if user is None:
        raise ValueError("User not found.")
    return user

