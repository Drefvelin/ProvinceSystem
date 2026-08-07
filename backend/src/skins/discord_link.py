"""Minecraft UUID ↔ Discord user id linking via one-time codes."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from .codes import generate_plaintext_code, hash_secret
from .db import connect


class LinkError(ValueError):
    """Invalid, expired, used, or conflicting Discord link."""


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_iso(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def _link_ttl_minutes() -> int:
    raw = os.environ.get("SKINS_LINK_TTL_MINUTES", "15").strip()
    try:
        return max(1, int(raw))
    except ValueError:
        return 15


def start_link(
    player_uuid: str, minecraft_name: str | None = None
) -> dict:
    uuid = (player_uuid or "").strip()
    if not uuid:
        raise LinkError("player_uuid is required")

    name = (minecraft_name or "").strip() or None
    plaintext = generate_plaintext_code()
    now = _utcnow()
    expires_at = _iso(now + timedelta(minutes=_link_ttl_minutes()))
    created_at = _iso(now)

    with connect() as conn:
        conn.execute(
            """
            INSERT INTO discord_link_codes (
                code_hash, player_uuid, minecraft_name, created_at, expires_at, used_at
            ) VALUES (?, ?, ?, ?, ?, NULL)
            """,
            (hash_secret(plaintext), uuid, name, created_at, expires_at),
        )
        conn.commit()

    return {"code": plaintext, "expires_at": expires_at}


def complete_link(code: str, discord_user_id: str) -> dict:
    plaintext = (code or "").strip()
    discord_id = (discord_user_id or "").strip()
    if not plaintext:
        raise LinkError("code is required")
    if not discord_id:
        raise LinkError("discord_user_id is required")

    code_hash = hash_secret(plaintext)
    now = _utcnow()
    linked_at = _iso(now)

    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM discord_link_codes WHERE code_hash = ?",
            (code_hash,),
        ).fetchone()

        if row is None:
            raise LinkError("Invalid link code")
        if row["used_at"]:
            raise LinkError("Link code has already been used")
        if _parse_iso(row["expires_at"]) < now:
            raise LinkError("Link code has expired")

        player_uuid = row["player_uuid"]
        minecraft_name = row["minecraft_name"]

        existing = conn.execute(
            "SELECT player_uuid FROM discord_links WHERE discord_user_id = ?",
            (discord_id,),
        ).fetchone()
        if existing is not None and existing["player_uuid"] != player_uuid:
            raise LinkError(
                "This Discord account is already linked to a different Minecraft player"
            )

        conn.execute(
            "DELETE FROM discord_links WHERE player_uuid = ?",
            (player_uuid,),
        )
        conn.execute(
            """
            INSERT INTO discord_links (
                player_uuid, discord_user_id, minecraft_name, linked_at
            ) VALUES (?, ?, ?, ?)
            """,
            (player_uuid, discord_id, minecraft_name, linked_at),
        )
        conn.execute(
            "UPDATE discord_link_codes SET used_at = ? WHERE id = ?",
            (linked_at, row["id"]),
        )
        conn.commit()

    return {
        "player_uuid": player_uuid,
        "discord_user_id": discord_id,
        "minecraft_name": minecraft_name,
        "linked_at": linked_at,
    }


def get_discord_id_for_uuid(player_uuid: str) -> str | None:
    uuid = (player_uuid or "").strip()
    if not uuid:
        return None
    with connect() as conn:
        row = conn.execute(
            "SELECT discord_user_id FROM discord_links WHERE player_uuid = ?",
            (uuid,),
        ).fetchone()
    if row is None:
        return None
    return str(row["discord_user_id"])


if __name__ == "__main__":
    from .db import migrate

    migrate()

    u1 = "00000000-0000-0000-0000-00000000a501"
    u2 = "00000000-0000-0000-0000-00000000a502"
    d1 = "111111111111111111"
    d2 = "222222222222222222"

    with connect() as conn:
        conn.execute("DELETE FROM discord_links WHERE player_uuid IN (?, ?)", (u1, u2))
        conn.execute(
            "DELETE FROM discord_link_codes WHERE player_uuid IN (?, ?)", (u1, u2)
        )
        conn.commit()

    started = start_link(u1, "TestPlayer")
    assert "code" in started and "expires_at" in started
    done = complete_link(started["code"], d1)
    assert done["player_uuid"] == u1
    assert done["discord_user_id"] == d1
    assert done["minecraft_name"] == "TestPlayer"
    assert get_discord_id_for_uuid(u1) == d1

    # Relink same UUID to new Discord id
    started2 = start_link(u1, "TestPlayer")
    complete_link(started2["code"], d2)
    assert get_discord_id_for_uuid(u1) == d2

    # Discord id taken by u1 — u2 cannot claim it
    started3 = start_link(u2)
    try:
        complete_link(started3["code"], d2)
    except LinkError:
        pass
    else:
        raise SystemExit("expected LinkError for discord already linked")

    # Reuse code
    try:
        complete_link(started2["code"], d1)
    except LinkError:
        pass
    else:
        raise SystemExit("expected LinkError for reused code")

    print("discord_link ok")
