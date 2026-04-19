"""Helpers for validating Supabase access tokens."""

from __future__ import annotations

import os

from fastapi import HTTPException
from supabase import Client, create_client


def _build_client() -> Client | None:
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_KEY", "").strip()
    if not url or not key:
        return None
    return create_client(url, key)


SUPABASE_CLIENT = _build_client()


def get_bearer_token(authorization: str | None) -> str:
    if not authorization:
        return ""

    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return ""
    return parts[1].strip()


def get_authenticated_user(authorization: str | None):
    token = get_bearer_token(authorization)
    if not token or SUPABASE_CLIENT is None:
        return None

    try:
        response = SUPABASE_CLIENT.auth.get_user(token)
    except Exception:
        return None

    return getattr(response, "user", None)


def require_authenticated_user(authorization: str | None):
    user = get_authenticated_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Bu işlem için giriş yapmalısınız.")
    return user
