"""Issue and redeem skins codes; opaque upload sessions."""

from __future__ import annotations

import hashlib
import os
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone

from .db import connect

SESSION_TTL_HOURS = 1


class CodeError(ValueError):
    """Invalid, expired, revoked, or already-redeemed code."""


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_iso(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def hash_secret(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def generate_plaintext_code() -> str:
    """Readable XXXX-XXXX-XXXX from hex groups."""
    raw = secrets.token_hex(6).upper()  # 12 hex chars
    return f"{raw[0:4]}-{raw[4:8]}-{raw[8:12]}"


def _code_ttl_hours() -> int:
    raw = os.environ.get("SKINS_CODE_TTL_HOURS", "48").strip()
    try:
        return max(1, int(raw))
    except ValueError:
        return 48


def issue_code(player_uuid: str) -> dict:
    uuid = (player_uuid or "").strip()
    if not uuid:
        raise CodeError("player_uuid is required")

    plaintext = generate_plaintext_code()
    now = _utcnow()
    expires = now + timedelta(hours=_code_ttl_hours())
    expires_at = _iso(expires)

    with connect() as conn:
        conn.execute(
            """
            INSERT INTO codes (code_hash, player_uuid, created_at, expires_at, redeemed_at, revoked)
            VALUES (?, ?, ?, ?, NULL, 0)
            """,
            (hash_secret(plaintext), uuid, _iso(now), expires_at),
        )
        conn.commit()

    return {"code": plaintext, "expires_at": expires_at}


def redeem_code(plaintext: str) -> dict:
    code = (plaintext or "").strip()
    if not code:
        raise CodeError("code is required")

    code_hash = hash_secret(code)
    now = _utcnow()

    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM codes WHERE code_hash = ?",
            (code_hash,),
        ).fetchone()

        if row is None:
            raise CodeError("Invalid code")
        if row["revoked"]:
            raise CodeError("Code has been revoked")
        if row["redeemed_at"]:
            raise CodeError("Code has already been redeemed")
        if _parse_iso(row["expires_at"]) < now:
            raise CodeError("Code has expired")

        session_token = secrets.token_urlsafe(32)
        session_expires = now + timedelta(hours=SESSION_TTL_HOURS)
        session_expires_at = _iso(session_expires)
        created_at = _iso(now)

        conn.execute(
            "UPDATE codes SET redeemed_at = ? WHERE id = ?",
            (created_at, row["id"]),
        )
        conn.execute(
            """
            INSERT INTO sessions (token_hash, code_id, player_uuid, expires_at, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                hash_secret(session_token),
                row["id"],
                row["player_uuid"],
                session_expires_at,
                created_at,
            ),
        )
        conn.commit()

    return {
        "session_token": session_token,
        "player_uuid": row["player_uuid"],
        "expires_at": session_expires_at,
        "code_id": row["id"],
    }


def get_session(token: str) -> sqlite3.Row | None:
    raw = (token or "").strip()
    if not raw:
        return None

    now = _utcnow()
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE token_hash = ?",
            (hash_secret(raw),),
        ).fetchone()

    if row is None:
        return None
    if _parse_iso(row["expires_at"]) < now:
        return None
    return row
