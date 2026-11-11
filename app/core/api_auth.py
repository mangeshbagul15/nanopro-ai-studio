"""Session gate for executive chat and action API routes.

The NanoPro manager chat can deploy, run pipelines and touch credentials, so a
public endpoint would let any stranger drive the host. Every executive route
accepts the same three credentials the rest of the app already issues:
X-Session-Token, an Authorization bearer token, or the nanopro_session cookie.
"""
from typing import Any, Dict

from fastapi import HTTPException, Request


def extract_session_token(request: Request) -> str:
    token = (request.headers.get("X-Session-Token") or "").strip()
    if not token:
        auth_header = (request.headers.get("Authorization") or "").strip()
        if auth_header.lower().startswith("bearer "):
            token = auth_header[7:].strip()
        elif auth_header:
            token = auth_header
    if not token:
        token = (request.cookies.get("nanopro_session") or "").strip()
    return token


def require_session(request: Request) -> Dict[str, Any]:
    """Returns the validated session user or raises 401."""
    token = extract_session_token(request)
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please log in to NanoPro AI Studio.",
        )
    from app.core.auth_manager import auth_manager

    result = auth_manager.validate_session(token) or {}
    user = result.get("user") or {}
    if not result.get("is_valid") or not user:
        raise HTTPException(
            status_code=401,
            detail="Session expired or invalid. Please log in again.",
        )
    return user


def require_admin_session(request: Request) -> Dict[str, Any]:
    """Returns the validated admin session user or raises 401/403."""
    user = require_session(request)
    if user.get("role") != "admin" and user.get("username") != "nanopro":
        raise HTTPException(
            status_code=403,
            detail="Super Admin access required for this action.",
        )
    return user
