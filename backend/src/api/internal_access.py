"""Access control for same-machine internal API routes."""

from __future__ import annotations

from fastapi import HTTPException, Request

LOCALHOST_HOSTS = frozenset({"127.0.0.1", "::1"})


def require_localhost(request: Request) -> None:
    host = request.client.host if request.client else ""
    if host not in LOCALHOST_HOSTS:
        raise HTTPException(status_code=403, detail="Localhost only")
