"""In-game plugin notice outbox (ArmourShop polls and delivers)."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from .db import connect


class PluginNoticeError(ValueError):
    """Notice not found or invalid."""


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def enqueue_link_success(
    player_uuid: str,
    *,
    discord_username: str | None = None,
    conn=None,
) -> int:
    """Enqueue a link_success notice. Optional conn shares caller's transaction."""
    uuid = (player_uuid or "").strip()
    if not uuid:
        raise PluginNoticeError("player_uuid is required")

    name = (discord_username or "").strip() or None
    payload = json.dumps({"discord_username": name})
    created_at = _iso_now()

    def _insert(c) -> int:
        cur = c.execute(
            """
            INSERT INTO plugin_notices (
                type, player_uuid, payload, created_at, delivered_at
            ) VALUES ('link_success', ?, ?, ?, NULL)
            """,
            (uuid, payload, created_at),
        )
        return int(cur.lastrowid)

    if conn is not None:
        return _insert(conn)

    with connect() as c:
        notice_id = _insert(c)
        c.commit()
        return notice_id


def list_undelivered_plugin_notices() -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM plugin_notices
            WHERE delivered_at IS NULL
            ORDER BY created_at ASC, id ASC
            """
        ).fetchall()

    result = []
    for row in rows:
        try:
            payload = json.loads(row["payload"])
        except (json.JSONDecodeError, TypeError):
            payload = {}
        result.append(
            {
                "id": row["id"],
                "type": row["type"],
                "player_uuid": row["player_uuid"],
                "payload": payload,
                "created_at": row["created_at"],
            }
        )
    return result


def ack_plugin_notices(ids: list[int]) -> dict:
    raw_ids = [int(i) for i in (ids or []) if i is not None]
    if not raw_ids:
        return {"acked": [], "delivered_at": None}

    now = _iso_now()
    acked: list[int] = []
    with connect() as conn:
        for notice_id in raw_ids:
            row = conn.execute(
                "SELECT id, delivered_at FROM plugin_notices WHERE id = ?",
                (notice_id,),
            ).fetchone()
            if row is None:
                continue
            if row["delivered_at"] is None:
                conn.execute(
                    "UPDATE plugin_notices SET delivered_at = ? WHERE id = ?",
                    (now, notice_id),
                )
            acked.append(notice_id)
        conn.commit()

    return {"acked": acked, "delivered_at": now if acked else None}
