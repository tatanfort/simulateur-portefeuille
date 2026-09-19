"""Password hashing + JWT bearer-token auth. Deliberately minimal: no
password reset flow, no email verification — just enough for a personal
tool to gate "save my portfolio" behind an account.
"""

import os
import secrets
import time

import bcrypt
import jwt
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

import models
from db import get_db

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    SECRET_KEY = secrets.token_hex(32)
    print(
        "WARNING: SECRET_KEY is not set — using a random key generated at startup. "
        "Existing sessions will be invalidated on every restart. Set the SECRET_KEY "
        "environment variable in production so logins persist across deploys."
    )

ALGORITHM = "HS256"
TOKEN_TTL_SECONDS = 30 * 24 * 3600  # 30 days


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def create_token(user_id: int) -> str:
    payload = {"sub": str(user_id), "exp": int(time.time()) + TOKEN_TTL_SECONDS}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    authorization: str = Header(default=None), db: Session = Depends(get_db)
) -> models.User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Non authentifié.")
    token = authorization[len("Bearer ") :]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Session invalide ou expirée.")
    user = db.get(models.User, int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable.")
    return user
