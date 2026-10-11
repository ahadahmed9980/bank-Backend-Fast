import hashlib
import uuid
from datetime import datetime, timedelta, timezone
import jwt

from app.config import JWT_SECRET, JWT_ALGORITHM


def create_access_token(user_id, session_id):
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


# Backward compatibility alias
creat_access_token = create_access_token


def create_refresh_token(user_id, session_id):
    payload = {
        "id": str(user_id),
        "sessionId": str(session_id),
        "type": "refresh",
        "jti": str(uuid.uuid4()),
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


def hash_refresh_token(refresh_token: str) -> str:
    return hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()
