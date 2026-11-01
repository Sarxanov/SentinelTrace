from datetime import UTC, datetime
from collections import defaultdict, deque
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ...api.dependencies import current_user, require_admin
from ...config import get_settings
from ...database import get_db
from ...models import User
from ...schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserRead
from ...services.auth_service import create_user, make_token, verify_password

router = APIRouter(prefix="/api/auth", tags=["authentication"])
_login_attempts: dict[str, deque[datetime]] = defaultdict(deque)


def _check_login_rate(request: Request) -> None:
    now = datetime.now(UTC)
    key = request.client.host if request.client else "unknown"
    attempts = _login_attempts[key]
    while attempts and (now - attempts[0]).total_seconds() > 60:
        attempts.popleft()
    if len(attempts) >= get_settings().login_rate_limit:
        raise HTTPException(429, "too many login attempts; try again later")
    attempts.append(now)


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest, response: Response, db: Annotated[Session, Depends(get_db)]):
    if db.scalar(select(func.count(User.id))) != 0:
        raise HTTPException(403, "registration is closed; an administrator must create accounts")
    try:
        user = create_user(db, payload.username, payload.password, "admin")
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    token = make_token(user, get_settings().auth_secret_runtime, get_settings().auth_token_ttl_minutes)
    response.set_cookie("sentineltrace_session", token, httponly=True, samesite="strict", secure=get_settings().cors_origins.startswith("https://"))
    return {"access_token": token, "user": user}


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, response: Response, request: Request, db: Annotated[Session, Depends(get_db)]):
    _check_login_rate(request)
    user = db.scalar(select(User).where(User.username == payload.username.lower(), User.is_active.is_(True)))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "invalid credentials")
    user.last_login_at = datetime.now(UTC)
    db.commit()
    token = make_token(user, get_settings().auth_secret_runtime, get_settings().auth_token_ttl_minutes)
    response.set_cookie("sentineltrace_session", token, httponly=True, samesite="strict", secure=request.url.scheme == "https")
    return {"access_token": token, "user": user}


@router.post("/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie("sentineltrace_session")


@router.get("/me", response_model=UserRead)
def me(user: Annotated[User, Depends(current_user)]):
    return user


@router.post("/users", response_model=UserRead, status_code=201)
def create_analyst(payload: RegisterRequest, db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(require_admin)]):
    try:
        return create_user(db, payload.username, payload.password)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
