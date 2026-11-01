import base64
import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import User

ALGORITHM = "scrypt"


def hash_password(password: str) -> str:
    if len(password) < 12:
        raise ValueError("password must be at least 12 characters")
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"{ALGORITHM}${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, salt_text, digest_text = encoded.split("$")
        if algorithm != ALGORITHM:
            return False
        salt = base64.urlsafe_b64decode(salt_text.encode())
        expected = base64.urlsafe_b64decode(digest_text.encode())
        actual = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def make_token(user: User, secret: str, ttl_minutes: int) -> str:
    expires = int((datetime.now(UTC) + timedelta(minutes=ttl_minutes)).timestamp())
    payload = f"{user.id}|{user.username}|{user.role}|{expires}"
    signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(f"{payload}|{signature}".encode()).decode()


def read_token(token: str, secret: str) -> dict[str, Any] | None:
    try:
        parts = base64.urlsafe_b64decode(token.encode()).decode().split("|")
        if len(parts) != 5:
            return None
        user_id, username, role, expires_text, signature = parts
        payload = "|".join(parts[:4])
        if not hmac.compare_digest(signature, hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()):
            return None
        if int(expires_text) < int(datetime.now(UTC).timestamp()):
            return None
        return {"id": user_id, "username": username, "role": role}
    except (ValueError, UnicodeError, TypeError):
        return None


def create_user(db: Session, username: str, password: str, role: str = "analyst") -> User:
    normalized = username.strip().lower()
    if not normalized or len(normalized) > 64:
        raise ValueError("username must be between 1 and 64 characters")
    if role not in {"analyst", "admin"}:
        raise ValueError("invalid role")
    if db.scalar(select(User).where(User.username == normalized)):
        raise ValueError("username already exists")
    user = User(username=normalized, password_hash=hash_password(password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
