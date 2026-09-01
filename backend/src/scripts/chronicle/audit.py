"""Audit trail for staff-triggered chronicle wipes and their restores.

The CLI wipe's real protection was that it needed shell access on the box. Once
the same operation is reachable from a browser session that protection is gone,
so the replacement is this table: every wipe records who asked for it, why, how
much went away and where the bytes were set aside. Nothing here deletes rows —
a restore stamps the existing row rather than clearing it.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from src.skins.db import connect, migrate

_TABLE = "map_chronicle_wipes"

# Explicit rather than `SELECT *`: `_row_to_record` unpacks by name, so the
# column order here is documentation, not a dependency, but a `SELECT *`
# would silently start returning any column a future migration adds to the
# table and make this the one place in the codebase that has to track that.
_COLUMNS = (
    "id",
    "map_id",
    "wiped_at",
    "wiped_by",
    "day_count",
    "backup_path",
    "reason",
    "restored_at",
    "restored_by",
)

_UNKNOWN_ACTOR = "unknown"


@dataclass(frozen=True)
class WipeRecord:
    id: int
    map_id: str
    wiped_at: int
    wiped_by: str
    day_count: int
    backup_path: str | None
    reason: str
    restored_at: int | None
    restored_by: str | None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "map_id": self.map_id,
            "wiped_at": self.wiped_at,
            "wiped_by": self.wiped_by,
            "day_count": self.day_count,
            "backup_path": self.backup_path,
            "reason": self.reason,
            "restored_at": self.restored_at,
            "restored_by": self.restored_by,
            "restored": self.restored_at is not None,
        }


def _row_to_record(row) -> WipeRecord:
    return WipeRecord(
        id=int(row["id"]),
        map_id=str(row["map_id"]),
        wiped_at=int(row["wiped_at"]),
        wiped_by=str(row["wiped_by"]),
        day_count=int(row["day_count"] or 0),
        backup_path=row["backup_path"],
        reason=str(row["reason"] or ""),
        restored_at=int(row["restored_at"]) if row["restored_at"] is not None else None,
        restored_by=row["restored_by"],
    )


def record_wipe(
    map_id: str,
    *,
    wiped_at: int,
    wiped_by: str,
    day_count: int,
    backup_path: str | None,
    reason: str,
) -> int:
    """Insert one audit row; returns its id (the handle a restore is asked for)."""
    migrate()
    conn = connect()
    try:
        with conn:
            cursor = conn.execute(
                f"INSERT INTO {_TABLE} "
                "(map_id, wiped_at, wiped_by, day_count, backup_path, reason) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    map_id,
                    int(wiped_at),
                    (wiped_by or "").strip() or _UNKNOWN_ACTOR,
                    int(day_count),
                    backup_path,
                    reason,
                ),
            )
        return int(cursor.lastrowid)
    finally:
        conn.close()


def list_wipes(map_id: str, limit: int = 100) -> list[WipeRecord]:
    """This map's wipe history, newest first. Never crosses map boundaries."""
    migrate()
    conn = connect()
    try:
        rows = conn.execute(
            f"SELECT {', '.join(_COLUMNS)} FROM {_TABLE} WHERE map_id = ? "
            "ORDER BY wiped_at DESC, id DESC LIMIT ?",
            (map_id, max(1, int(limit))),
        ).fetchall()
    finally:
        conn.close()
    return [_row_to_record(row) for row in rows]


def get_wipe(map_id: str, wipe_id: int) -> WipeRecord | None:
    """One audit row, scoped to the map — an id from another map reads as absent."""
    migrate()
    conn = connect()
    try:
        row = conn.execute(
            f"SELECT {', '.join(_COLUMNS)} FROM {_TABLE} WHERE id = ? AND map_id = ?",
            (int(wipe_id), map_id),
        ).fetchone()
    finally:
        conn.close()
    return _row_to_record(row) if row is not None else None


def last_wiped_at(map_id: str) -> int | None:
    """Newest wipe stamp for this map, or None if it has never been wiped.

    This is what lets a viewer tell "wiped" apart from "never captured": both
    leave the chronicle index with `days: []`.

    Deliberately does not call `migrate()`: this runs on every chronicle index
    request, and re-running the whole schema script per request is not something
    a read route should pay for. A database that predates the table degrades to
    None — the index loses one additive field rather than returning a 500.
    """
    conn = connect()
    try:
        row = conn.execute(
            f"SELECT MAX(wiped_at) AS stamp FROM {_TABLE} WHERE map_id = ?",
            (map_id,),
        ).fetchone()
    except sqlite3.OperationalError:
        return None
    finally:
        conn.close()
    if row is None or row["stamp"] is None:
        return None
    return int(row["stamp"])


def mark_restored(map_id: str, wipe_id: int, *, restored_at: int, restored_by: str) -> None:
    """Stamp the restore bookkeeping. Scoped by map_id as well as id."""
    migrate()
    conn = connect()
    try:
        with conn:
            conn.execute(
                f"UPDATE {_TABLE} SET restored_at = ?, restored_by = ? "
                "WHERE id = ? AND map_id = ?",
                (
                    int(restored_at),
                    (restored_by or "").strip() or _UNKNOWN_ACTOR,
                    int(wipe_id),
                    map_id,
                ),
            )
    finally:
        conn.close()
