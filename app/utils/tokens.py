import hashlib
from datetime import datetime, timedelta, timezone
import jwt

from app.config import JWT_SECRET

JWT_ALGORITHM = "HS256"


def creat_access_token(user_id, session_id):
    payload = {
        "id": str(user_id),
        "sessionId": str(session_id),
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=10),
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


def create_refresh_token(user_id, session_id):
    payload = {
        "id": str(user_id),
        "sessionId": str(session_id),
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


def hash_refresh_token(refresh_token: str) -> str:
    return hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()
