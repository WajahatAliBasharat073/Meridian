"""Auth. Single user today, but wired properly: a real bearer token is
verified against Supabase's JWT secret when one is configured; local dev
without a secret falls back to one stub user so the API is usable before
Supabase Auth is wired to the frontend."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt

from app.config import Settings, get_settings

# Stable, arbitrary UUID for local dev only — never used once
# SUPABASE_JWT_SECRET is set.
STUB_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


async def get_current_user_id(
    authorization: Annotated[str | None, Header()] = None,
    settings: Annotated[Settings, Depends(get_settings)] = None,  # type: ignore[assignment]
) -> uuid.UUID:
    settings = settings or get_settings()

    if not settings.supabase_jwt_secret:
        return STUB_USER_ID

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    token = authorization.removeprefix("Bearer ")
    try:
        payload = jwt.decode(
            token, settings.supabase_jwt_secret, algorithms=["HS256"], options={"verify_aud": False}
        )
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing subject")
    return uuid.UUID(sub)
