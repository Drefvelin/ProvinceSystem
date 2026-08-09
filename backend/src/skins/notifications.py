"""Staff-facing skin notification outbox (player DMs via bot)."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from .db import connect


class NotificationError(ValueError):
    """Notification not found or invalid."""


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def enqueue_submitted(
    submission_id: str,
    discord_user_id: str,
    *,
    display_name: str,
    kind: str,
    slug: str,
) -> int:
    payload = json.dumps(
        {
            "submission_id": submission_id,
            "display_name": display_name,
            "kind": kind,
            "slug": slug,
        }
    )
    created_at = _iso_now()
    with connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO skin_notifications (
                type, submission_id, discord_user_id, payload, created_at, delivered_at
            ) VALUES ('submitted', ?, ?, ?, ?, NULL)
            """,
            (submission_id, discord_user_id, payload, created_at),
        )
        conn.commit()
        return int(cur.lastrowid)


def list_undelivered() -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM skin_notifications
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
                "submission_id": row["submission_id"],
                "discord_user_id": row["discord_user_id"],
                "payload": payload,
                "created_at": row["created_at"],
            }
        )
    return result


def ack_notification(notification_id: int) -> dict:
    now = _iso_now()
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM skin_notifications WHERE id = ?",
            (notification_id,),
        ).fetchone()
        if row is None:
            raise NotificationError("Notification not found")
        if row["delivered_at"] is None:
            conn.execute(
                "UPDATE skin_notifications SET delivered_at = ? WHERE id = ?",
                (now, notification_id),
            )
            conn.commit()
            delivered_at = now
        else:
            delivered_at = row["delivered_at"]

    return {"id": notification_id, "delivered_at": delivered_at}
