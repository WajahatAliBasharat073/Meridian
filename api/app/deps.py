"""Auth. Single user today, but wired properly.

Supabase now defaults new projects to asymmetric JWT signing keys
(ES256/RS256, verified via the project's JWKS endpoint) rather than the
legacy HS256 shared secret — a real session token's `alg` header decides
which path applies here, so both are supported rather than assuming the
older scheme. Local dev without either configured falls back to one stub
user.
"""

from __future__ import annotations

import time
import uuid
from typing import Annotated, Any

import httpx
from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db import get_session
from app.models.core import User

# Stable, arbitrary UUID for local dev only — never used once real auth
# (either verification path below) is configured.
STUB_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

_JWKS_TTL_SECONDS = 3600
_jwks_cache: dict[str, Any] = {"keys": [], "fetched_at": 0.0}

# A real Supabase Auth user has no corresponding local `users` row until
# their first authenticated request — there is no signup webhook wiring
# it up ahead of time. Once confirmed to exist, skip the check on every
# later request rather than re-querying per-request.
_known_user_ids: set[uuid.UUID] = set()


async def _ensure_user_row(session: AsyncSession, user_id: uuid.UUID, email: str | None) -> None:
    if user_id in _known_user_ids:
        return
    existing = (await session.execute(select(User.id).where(User.id == user_id))).first()
    if existing is None:
        session.add(User(id=user_id, email=email or f"{user_id}@unknown.local", settings={}))
        try:
            await session.commit()
        except IntegrityError:
            # Two concurrent first-requests both saw "not found" and both
            # tried to insert — the loser just means the row exists now.
            await session.rollback()
    _known_user_ids.add(user_id)


async def _get_jwks(supabase_url: str, *, force_refresh: bool = False) -> list[dict[str, Any]]:
    now = time.time()
    if (
        not force_refresh
        and _jwks_cache["keys"]
        and (now - _jwks_cache["fetched_at"]) < _JWKS_TTL_SECONDS
    ):
        return list(_jwks_cache["keys"])

    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get(f"{supabase_url}/auth/v1/.well-known/jwks.json")
        resp.raise_for_status()
        keys = resp.json().get("keys", [])

    _jwks_cache["keys"] = keys
    _jwks_cache["fetched_at"] = now
    return list(keys)


async def _verify_asymmetric(token: str, header: dict[str, Any], settings: Settings) -> dict[str, Any]:
    if not settings.supabase_url:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="SUPABASE_URL not configured — cannot verify this token's signing key",
        )

    kid = header.get("kid")
    keys = await _get_jwks(settings.supabase_url)
    matching = next((k for k in keys if k.get("kid") == kid), None)

    if matching is None:
        # Key rotation: refetch once before giving up.
        keys = await _get_jwks(settings.supabase_url, force_refresh=True)
        matching = next((k for k in keys if k.get("kid") == kid), None)

    if matching is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown signing key")

    try:
        return dict(
            jwt.decode(token, matching, algorithms=[header["alg"]], options={"verify_aud": False})
        )
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


async def get_current_user_id(
    authorization: Annotated[str | None, Header()] = None,
    settings: Annotated[Settings, Depends(get_settings)] = None,  # type: ignore[assignment]
    session: Annotated[AsyncSession, Depends(get_session)] = None,  # type: ignore[assignment]
) -> uuid.UUID:
    settings = settings or get_settings()

    if not settings.supabase_jwt_secret and not settings.supabase_url:
        return STUB_USER_ID

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    token = authorization.removeprefix("Bearer ")

    try:
        header = jwt.get_unverified_header(token)
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed token") from exc

    if header.get("alg") == "HS256":
        if not settings.supabase_jwt_secret:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="SUPABASE_JWT_SECRET not configured — cannot verify an HS256 token",
            )
        try:
            payload = dict(
                jwt.decode(
                    token,
                    settings.supabase_jwt_secret,
                    algorithms=["HS256"],
                    options={"verify_aud": False},
                )
            )
        except JWTError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    else:
        payload = await _verify_asymmetric(token, header, settings)

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing subject")
    user_id = uuid.UUID(sub)
    await _ensure_user_row(session, user_id, payload.get("email"))
    return user_id
