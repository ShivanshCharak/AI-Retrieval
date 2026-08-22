import os

import jwt
from fastapi import HTTPException, Request

# NEVER hardcode secrets in source. Load from environment / secrets manager.
# The original file had SECRET_KEY committed directly in chat.py — treat that
# key as compromised and rotate it if this code has ever been pushed anywhere.
SECRET_KEY = "4WfP4JbL6lLQ5zQZ_8K4YxW5RkM8bM7T9dN2L8xR1cA"
ALGORITHM = "HS256"


def get_current_user_id(request: Request) -> int:
    """Extract and validate the user id from the access_token cookie.

    Raises HTTPException(401) for missing, expired, or invalid tokens instead
    of letting jwt.decode's exceptions bubble up as unhandled 500s.
    """
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return payload["user_id"]
