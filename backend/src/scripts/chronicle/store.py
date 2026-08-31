"""Chronicle storage layout + SQLite index for daily map snapshots."""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone

from src.api.map_registry import get_map_entry
from src.skins.codes import CodeError, normalize_realm_id
from src.skins.db import connect

from ..util.dirs import OUTPUT_DIR, defines_file, validate_map

# The set of source files a snapshot captures. Order is the manifest order.
CHRONICLE_FILES: tuple[str, ...] = (
    "nation",
    "province_data",
    "map_markers",
    "trade",
    "guilds",
    "zoc_overlays",
)

_DAY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# A `same_as` chain should be one hop in practice; the bound only exists so
# corrupt/cyclic manifests cannot spin the server.
_MAX_SAME_AS_HOPS = 64

_DEFAULT_REALM_ID = "main"


def chronicle_root(map_name: str) -> str:
    validate_map(map_name)
    return os.path.join(OUTPUT_DIR, map_name, "chronicle")


def chronicle_day_dir(map_name: str, day: str) -> str:
    if not is_valid_day(day):
        raise ValueError("Invalid chronicle day")
    return os.path.join(chronicle_root(map_name), day)


def stored_file_path(map_name: str, day: str, name: str) -> str:
    if name not in CHRONICLE_FILES:
        raise ValueError(f"Unknown chronicle file '{name}'")
    return os.path.join(chronicle_day_dir(map_name, day), f"{name}.json.gz")


def today_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def is_valid_day(day: str) -> bool:
    """Strict YYYY-MM-DD — also rejects real-looking but invalid dates."""
    if not isinstance(day, str) or not _DAY_RE.match(day):
        return False
    try:
        datetime.strptime(day, "%Y-%m-%d")
    except ValueError:
        return False
    return True


def geometry_version(map_name: str) -> str | None:
    """sha256 of the static province geometry, or None if not generated yet."""
    validate_map(map_name)
    path = defines_file(map_name, "province_id_runs.bin.gz")
    if not os.path.exists(path):
        return None
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def realm_for_map(map_name: str) -> str:
    validate_map(map_name)
    entry = get_map_entry(map_name)
    if entry is None:
        return _DEFAULT_REALM_ID
    try:
        return normalize_realm_id(getattr(entry, "realm_id", None))
    except CodeError:
        # An unusable realm in maps.yml must not block history accruing.
        return _DEFAULT_REALM_ID


def _snapshot_row(conn, map_id: str, day: str) -> dict | None:
    """Read one indexed snapshot on a caller-owned connection."""
    row = conn.execute(
        "SELECT map_id, day, realm_id, captured_at, bytes, "
        "geometry_version, manifest FROM map_chronicle_snapshots "
        "WHERE map_id = ? AND day = ?",
        (map_id, day),
    ).fetchone()
    if row is None:
        return None
    try:
        manifest = json.loads(row["manifest"])
    except (TypeError, ValueError):
        manifest = {}
    return {
        "map_id": row["map_id"],
        "day": row["day"],
        "realm_id": row["realm_id"],
        "captured_at": row["captured_at"],
        "bytes": row["bytes"],
        "geometry_version": row["geometry_version"],
        "manifest": manifest,
    }


def upsert_snapshot(
    map_id: str,
    day: str,
    realm_id: str,
    captured_at: int,
    byte_count: int,
    geometry_version: str | None,
    manifest: dict,
) -> None:
    validate_map(map_id)
    if not is_valid_day(day):
        raise ValueError("Invalid chronicle day")
    conn = connect()
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO map_chronicle_snapshots
                    (map_id, day, realm_id, captured_at, bytes,
                     geometry_version, manifest)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(map_id, day) DO UPDATE SET
                    realm_id = excluded.realm_id,
                    captured_at = excluded.captured_at,
                    bytes = excluded.bytes,
                    geometry_version = excluded.geometry_version,
                    manifest = excluded.manifest
                """,
                (
                    map_id,
                    day,
                    realm_id,
                    int(captured_at),
                    int(byte_count),
                    geometry_version,
                    json.dumps(manifest, ensure_ascii=False),
                ),
            )
    finally:
        conn.close()


def latest_day(map_id: str) -> str | None:
    validate_map(map_id)
    conn = connect()
    try:
        row = conn.execute(
            "SELECT day FROM map_chronicle_snapshots WHERE map_id = ? "
            "ORDER BY day DESC LIMIT 1",
            (map_id,),
        ).fetchone()
        return row["day"] if row else None
    finally:
        conn.close()


def list_days(map_id: str) -> list[str]:
    validate_map(map_id)
    conn = connect()
    try:
        rows = conn.execute(
            "SELECT day FROM map_chronicle_snapshots WHERE map_id = ? "
            "ORDER BY day ASC",
            (map_id,),
        ).fetchall()
        return [row["day"] for row in rows]
    finally:
        conn.close()


def get_snapshot(map_id: str, day: str) -> dict | None:
    validate_map(map_id)
    if not is_valid_day(day):
        return None
    conn = connect()
    try:
        return _snapshot_row(conn, map_id, day)
    finally:
        conn.close()


def previous_snapshot(map_id: str, day: str) -> dict | None:
    """Newest snapshot strictly before `day` — the dedup baseline for a capture."""
    validate_map(map_id)
    if not is_valid_day(day):
        raise ValueError("Invalid chronicle day")
    conn = connect()
    try:
        row = conn.execute(
            "SELECT day FROM map_chronicle_snapshots "
            "WHERE map_id = ? AND day < ? ORDER BY day DESC LIMIT 1",
            (map_id, day),
        ).fetchone()
        return _snapshot_row(conn, map_id, row["day"]) if row else None
    finally:
        conn.close()


def days_referencing(map_id: str, day: str) -> list[str]:
    """Days *after* `day` whose manifest resolves a file through it.

    `previous_snapshot` only ever looks backwards, so nothing else in the
    capture path can see that later days are depending on this day's bytes.
    Overwriting `day` would silently change what those days serve — their own
    recorded sha256 would still describe the old content and no reader hashes
    on the way out. Callers use this to refuse the overwrite instead.
    """
    validate_map(map_id)
    if not is_valid_day(day):
        raise ValueError("Invalid chronicle day")
    conn = connect()
    try:
        rows = conn.execute(
            "SELECT day, manifest FROM map_chronicle_snapshots "
            "WHERE map_id = ? AND day > ? ORDER BY day ASC",
            (map_id, day),
        ).fetchall()
    finally:
        conn.close()

    referencing: list[str] = []
    for row in rows:
        try:
            manifest = json.loads(row["manifest"])
        except (TypeError, ValueError):
            # An unreadable manifest cannot be shown to point here, but it also
            # cannot be shown not to — treat it as a blocker, not as absent.
            referencing.append(row["day"])
            continue
        files = manifest.get("files") or {}
        if any(
            isinstance(entry, dict) and entry.get("same_as") == day
            for entry in files.values()
        ):
            referencing.append(row["day"])
    return referencing


def resolve_stored_file(map_name: str, day: str, name: str) -> str | None:
    """Path to the bytes for (day, name), following `same_as` back-pointers."""
    validate_map(map_name)
    if name not in CHRONICLE_FILES or not is_valid_day(day):
        return None

    conn = connect()
    try:
        seen: set[str] = set()
        current = day
        for _ in range(_MAX_SAME_AS_HOPS):
            if current in seen:
                return None
            seen.add(current)

            snapshot = _snapshot_row(conn, map_name, current)
            if snapshot is None:
                return None
            entry = (snapshot["manifest"].get("files") or {}).get(name)
            if not isinstance(entry, dict):
                return None

            same_as = entry.get("same_as")
            if same_as:
                if not is_valid_day(same_as):
                    return None
                current = same_as
                continue

            path = stored_file_path(map_name, current, name)
            return path if os.path.exists(path) else None
        return None
    finally:
        conn.close()
