"""Character roster mirror pushed by RPCharacters."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class RosterError(ValueError):
    """Invalid roster payload."""


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def count_alive(player_uuid: str) -> int:
    from src.skins.db import connect

    uuid = (player_uuid or "").strip()
    if not uuid:
        return 0
    with connect() as conn:
        row = conn.execute(
            """
            SELECT COUNT(*) AS n FROM character_roster
            WHERE player_uuid = ? AND LOWER(status) = 'alive'
            """,
            (uuid,),
        ).fetchone()
    return int(row["n"] if row else 0)


def list_roster(player_uuid: str) -> list[dict[str, Any]]:
    from src.skins.db import connect

    uuid = (player_uuid or "").strip()
    if not uuid:
        return []
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT character_id, name, status, race, class, created_at, updated_at
            FROM character_roster
            WHERE player_uuid = ?
            ORDER BY created_at ASC, character_id ASC
            """,
            (uuid,),
        ).fetchall()
    return [
        {
            "id": row["character_id"],
            "name": row["name"],
            "status": row["status"],
            "race": row["race"],
            "class": row["class"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "source": "roster",
        }
        for row in rows
    ]


def replace_roster(player_uuid: str, characters: list) -> dict[str, Any]:
    from src.skins.db import connect

    uuid = (player_uuid or "").strip()
    if not uuid:
        raise RosterError("player_uuid is required")
    if not isinstance(characters, list):
        raise RosterError("characters must be a list")

    now = _iso_now()
    normalized: list[tuple] = []
    seen: set[str] = set()
    for i, raw in enumerate(characters):
        if not isinstance(raw, dict):
            raise RosterError(f"characters[{i}] must be an object")
        cid = str(raw.get("id") or "").strip()
        name = str(raw.get("name") or "").strip()
        status = str(raw.get("status") or "").strip().upper()
        if not cid:
            raise RosterError(f"characters[{i}].id is required")
        if not name:
            raise RosterError(f"characters[{i}].name is required")
        if not status:
            raise RosterError(f"characters[{i}].status is required")
        if cid in seen:
            raise RosterError(f"duplicate character id: {cid}")
        seen.add(cid)
        race = raw.get("race")
        klass = raw.get("class")
        created_at = raw.get("created_at")
        normalized.append(
            (
                uuid,
                cid,
                name,
                status,
                str(race).strip() if race is not None else None,
                str(klass).strip() if klass is not None else None,
                str(created_at).strip() if created_at is not None else None,
                now,
            )
        )

    with connect() as conn:
        conn.execute(
            "DELETE FROM character_roster WHERE player_uuid = ?",
            (uuid,),
        )
        conn.executemany(
            """
            INSERT INTO character_roster (
                player_uuid, character_id, name, status, race, class,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            normalized,
        )
        conn.commit()

    return {"ok": True, "player_uuid": uuid, "count": len(normalized)}
