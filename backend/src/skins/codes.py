"""Issue and redeem skins codes; opaque upload sessions."""

from __future__ import annotations

import hashlib
import os
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone

from .db import connect

SESSION_TTL_HOURS = 1
ALLOWED_SCOPES = frozenset({"skin", "character"})


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


def _normalize_scope(scope: str | None) -> str:
    raw = (scope or "skin").strip().lower()
    if not raw:
        raw = "skin"
    if raw not in ALLOWED_SCOPES:
        raise CodeError("scope must be 'skin' or 'character'")
    return raw


def _row_scope(row) -> str:
    try:
        value = row["scope"]
    except (KeyError, IndexError):
        return "skin"
    if value is None:
        return "skin"
    text = str(value).strip().lower()
    return text if text else "skin"


def issue_code(player_uuid: str, scope: str | None = "skin") -> dict:
    from .discord_link import get_identity_status

    uuid = (player_uuid or "").strip()
    if not uuid:
        raise CodeError("player_uuid is required")
    normalized = _normalize_scope(scope)

    status = get_identity_status(uuid)
    if not status.get("eligible"):
        raise CodeError("Link Discord in-game with /linkdiscord first")

    plaintext = generate_plaintext_code()
    now = _utcnow()
    expires = now + timedelta(hours=_code_ttl_hours())
    expires_at = _iso(expires)

    with connect() as conn:
        conn.execute(
            """
            INSERT INTO codes (
                code_hash, code_plaintext, player_uuid, scope, created_at, expires_at,
                redeemed_at, revoked
            )
            VALUES (?, ?, ?, ?, ?, ?, NULL, 0)
            """,
            (
                hash_secret(plaintext),
                plaintext,
                uuid,
                normalized,
                _iso(now),
                expires_at,
            ),
        )
        conn.commit()

    return {"code": plaintext, "expires_at": expires_at, "scope": normalized}


def list_active_codes() -> list[dict]:
    """Unused, unrevoked, unexpired codes that still have plaintext."""
    now = _iso(_utcnow())
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT
                c.code_plaintext AS code,
                c.player_uuid AS player_uuid,
                c.scope AS scope,
                d.minecraft_name AS minecraft_name,
                c.created_at AS created_at,
                c.expires_at AS expires_at
            FROM codes c
            LEFT JOIN discord_links d ON d.player_uuid = c.player_uuid
            WHERE c.revoked = 0
              AND c.redeemed_at IS NULL
              AND c.expires_at > ?
              AND c.code_plaintext IS NOT NULL
              AND TRIM(c.code_plaintext) != ''
            ORDER BY c.created_at ASC
            """,
            (now,),
        ).fetchall()
    return [
        {
            "code": row["code"],
            "player_uuid": row["player_uuid"],
            "scope": _row_scope(row),
            "minecraft_name": row["minecraft_name"],
            "created_at": row["created_at"],
            "expires_at": row["expires_at"],
        }
        for row in rows
    ]


def revoke_code(plaintext: str) -> dict:
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
            raise CodeError("Code has already been revoked")
        if row["redeemed_at"]:
            raise CodeError("Code has already been redeemed")
        if _parse_iso(row["expires_at"]) < now:
            raise CodeError("Code has expired")

        conn.execute(
            "UPDATE codes SET revoked = 1 WHERE id = ?",
            (row["id"],),
        )
        conn.commit()

    return {"ok": True, "code": code}


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
        if _row_scope(row) != "skin":
            raise CodeError("This code is for character creation, not skins")

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


def _self_test() -> None:
    """Mint/redeem scope checks. Run: python -m src.skins.codes"""
    from .db import migrate
    from .discord_link import LinkError, complete_link, start_link, unlink_by_uuid

    migrate()
    uuid = "00000000-0000-4000-8000-000000000105"
    discord_id = "discord-scope-selftest-105"
    try:
        unlink_by_uuid(uuid)
    except LinkError:
        pass

    try:
        issue_code(uuid, "skin")
        raise AssertionError("expected unlinked mint to fail")
    except CodeError as e:
        assert "Link Discord" in str(e)

    start = start_link(uuid, "ScopeTest")
    assert "code" in start
    complete_link(start["code"], discord_id, "ScopeTestUser")

    skin = issue_code(uuid, "skin")
    assert skin["scope"] == "skin" and skin["code"]
    session = redeem_code(skin["code"])
    assert session.get("session_token")

    char = issue_code(uuid, "character")
    assert char["scope"] == "character"
    try:
        redeem_code(char["code"])
        raise AssertionError("expected character code skins redeem to fail")
    except CodeError as e:
        assert "character creation" in str(e).lower()

    try:
        issue_code(uuid, "bogus")
        raise AssertionError("expected bad scope to fail")
    except CodeError as e:
        assert "scope" in str(e).lower()

    # default scope (ArmourShop back-compat)
    defaulted = issue_code(uuid)
    assert defaulted["scope"] == "skin"

    try:
        unlink_by_uuid(uuid)
    except LinkError:
        pass
    print("codes scope self-test OK")


if __name__ == "__main__":
    _self_test()
