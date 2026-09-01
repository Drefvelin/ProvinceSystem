"""Ledger storage layout + SQLite index for economy snapshots.

Layout mirrors the chronicle's: paths are derived, never stored, and every
function connects and closes for itself unless a caller hands it a connection
(`open_connection`) to group several writes into one transaction. Range reads
are one ordered SELECT — see `read_faction_days` for why per-day queries are
forbidden here.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone

from src.skins.db import connect

from ..util.dirs import OUTPUT_DIR, validate_map

_DAY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Column order is shared between the writer and every reader so a row can be
# turned back into a dict without naming the columns twice.
FACTION_DAY_COLUMNS: tuple[str, ...] = (
    "faction_key",
    "faction_id",
    "founded_at",
    "name",
    "rgb",
    "overlord",
    "wealth",
    "bank",
    "vassal_wealth",
    "net_income",
    "inflation_delta",
    "trade_power",
    "prestige",
    "rank",
    "rank_level",
    "rank_up_at",
    "rank_down_at",
    "prestige_position",
    "wealth_position",
    "provinces",
    "realm_size",
    "tier",
    "tier_index",
    "highest_title",
    "members",
    "members_with_vassals",
    "settlements",
    "population",
    "installations",
    "forts",
)
_FACTION_DAY_JSON_COLUMNS: tuple[str, ...] = (
    "wealth_breakdown",
    "prestige_breakdown",
    "subjects",
    "wars",
)

GUILD_DAY_COLUMNS: tuple[str, ...] = (
    "guild_id",
    "faction_id",
    "name",
    "type",
    "wealth",
    "bank",
    "expansions",
    "trade_power",
    "credit_score",
    "size",
)

# The snapshot names these two `key`/`id`; the column names carry the "faction"
# prefix so a joined row stays readable.
_FACTION_COLUMN_SOURCE = {"faction_key": "key", "faction_id": "id"}

_REGISTRY_COLUMNS: tuple[str, ...] = (
    "faction_key",
    "faction_id",
    "founded_at",
    "first_seen_day",
    "first_seen_at",
    "last_seen_day",
    "last_seen_at",
    "last_name",
    "last_rgb",
    "deleted_day",
    "deleted_at",
)

_DAY_COLUMNS: tuple[str, ...] = (
    "day",
    "captured_at",
    "captured_at_ts",
    "server_day",
    "day_progress_seconds",
    "complete",
    "schema_version",
    "faction_count",
    "guild_count",
)


def _empty_for(column: str):
    return {} if column.endswith("breakdown") else []


def _json_column(faction: dict, column: str) -> str:
    value = faction.get(column)
    if not isinstance(value, (dict, list)):
        value = _empty_for(column)
    return json.dumps(value, ensure_ascii=False)


def _quote(column: str) -> str:
    """`rank` is a SQLite window function name; quote every column uniformly."""
    return f'"{column}"'


def open_connection():
    """A connection the caller owns, for running several writes as one unit.

    Every function here still connects and closes for itself when `conn` is
    omitted. Pass one in — inside a single `with conn:` — when a group of writes
    must become visible together; `ingest.index_snapshot` is the reason this
    exists.
    """
    return connect()


def _write(conn, action):
    """Run `action(conn)`, owning the connection and transaction if none given."""
    if conn is not None:
        return action(conn)
    owned = connect()
    try:
        with owned:
            return action(owned)
    finally:
        owned.close()


# --- paths -------------------------------------------------------------------


def ledger_root(map_name: str) -> str:
    validate_map(map_name)
    return os.path.join(OUTPUT_DIR, map_name, "ledger")


def ledger_lock_path(map_name: str) -> str:
    """The per-map ledger lock file — a sibling of the tree, never inside it.

    A wipe renames `ledger/` aside, so a lock file living under it would be
    carried off mid-operation and the next acquire would create a fresh one.
    """
    return ledger_root(map_name) + ".lock"


def raw_root(map_name: str) -> str:
    return os.path.join(ledger_root(map_name), "raw")


def raw_day_dir(map_name: str, day: str) -> str:
    if not is_valid_day(day):
        raise ValueError("Invalid ledger day")
    return os.path.join(raw_root(map_name), day)


def raw_snapshot_path(map_name: str, day: str, hhmmss: str, sha8: str) -> str:
    return os.path.join(raw_day_dir(map_name, day), f"{hhmmss}Z-{sha8}.json.gz")


def daily_root(map_name: str) -> str:
    return os.path.join(ledger_root(map_name), "daily")


def daily_path(map_name: str, day: str) -> str:
    if not is_valid_day(day):
        raise ValueError("Invalid ledger day")
    return os.path.join(daily_root(map_name), f"{day}.json.gz")


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


# --- writes ------------------------------------------------------------------


def upsert_day(map_id: str, snapshot: dict, *, conn=None) -> None:
    """Record `snapshot` as the canonical daily row for its UTC day."""
    validate_map(map_id)
    day = snapshot["day"]
    if not is_valid_day(day):
        raise ValueError("Invalid ledger day")

    def action(conn):
        conn.execute(
            """
            INSERT INTO map_ledger_days
                (map_id, day, captured_at, captured_at_ts, server_day,
                 day_progress_seconds, complete, schema_version,
                 faction_count, guild_count, globals)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(map_id, day) DO UPDATE SET
                captured_at = excluded.captured_at,
                captured_at_ts = excluded.captured_at_ts,
                server_day = excluded.server_day,
                day_progress_seconds = excluded.day_progress_seconds,
                complete = excluded.complete,
                schema_version = excluded.schema_version,
                faction_count = excluded.faction_count,
                guild_count = excluded.guild_count,
                globals = excluded.globals
            """,
            (
                map_id,
                day,
                snapshot["captured_at"],
                int(snapshot["captured_at_ts"]),
                snapshot.get("server_day"),
                snapshot.get("day_progress_seconds"),
                1 if snapshot.get("complete") else 0,
                int(snapshot.get("schema_version") or 0),
                len(snapshot.get("factions") or []),
                len(snapshot.get("guilds") or []),
                json.dumps(snapshot.get("global") or {}, ensure_ascii=False),
            ),
        )

    _write(conn, action)


def replace_day_factions(
    map_id: str, day: str, factions: list[dict], *, conn=None
) -> None:
    """Swap this day's faction rows wholesale, inside one transaction.

    Delete-then-insert rather than upsert: a faction that left between two
    promotions of the same day must not survive as a stale row.
    """
    validate_map(map_id)
    if not is_valid_day(day):
        raise ValueError("Invalid ledger day")
    columns = ("map_id", "day", *FACTION_DAY_COLUMNS, *_FACTION_DAY_JSON_COLUMNS)
    placeholders = ", ".join("?" * len(columns))
    sql = (
        f"INSERT INTO map_ledger_faction_days ({', '.join(_quote(c) for c in columns)}) "
        f"VALUES ({placeholders})"
    )
    rows = [
        (
            map_id,
            day,
            *(
                faction.get(_FACTION_COLUMN_SOURCE.get(column, column))
                for column in FACTION_DAY_COLUMNS
            ),
            *(_json_column(faction, column) for column in _FACTION_DAY_JSON_COLUMNS),
        )
        for faction in factions
    ]

    def action(conn):
        conn.execute(
            "DELETE FROM map_ledger_faction_days WHERE map_id = ? AND day = ?",
            (map_id, day),
        )
        if rows:
            conn.executemany(sql, rows)

    _write(conn, action)


def replace_day_guilds(
    map_id: str, day: str, guilds: list[dict], *, conn=None
) -> None:
    validate_map(map_id)
    if not is_valid_day(day):
        raise ValueError("Invalid ledger day")
    columns = ("map_id", "day", *GUILD_DAY_COLUMNS)
    placeholders = ", ".join("?" * len(columns))
    sql = (
        f"INSERT INTO map_ledger_guild_days ({', '.join(_quote(c) for c in columns)}) "
        f"VALUES ({placeholders})"
    )
    rows = [
        (
            map_id,
            day,
            guild.get("id"),
            *(guild.get(column) for column in GUILD_DAY_COLUMNS[1:]),
        )
        for guild in guilds
    ]

    def action(conn):
        conn.execute(
            "DELETE FROM map_ledger_guild_days WHERE map_id = ? AND day = ?",
            (map_id, day),
        )
        if rows:
            conn.executemany(sql, rows)

    _write(conn, action)


def touch_registry(
    map_id: str, day: str, captured_at: str, factions: list[dict], *, conn=None
) -> None:
    """Insert/refresh registry rows for every faction present on `day`.

    `first_seen_*` is written once on insert and never moved; name and rgb are
    display fields and always take the newest value. A row that reappears has
    its `deleted_*` cleared — the faction was never gone, only absent from an
    incomplete snapshot, or it came back.
    """
    validate_map(map_id)
    if not is_valid_day(day):
        raise ValueError("Invalid ledger day")
    if not factions:
        return
    rows = [
        (
            map_id,
            faction["key"],
            faction["id"],
            faction["founded_at"],
            day,
            captured_at,
            day,
            captured_at,
            faction.get("name"),
            faction.get("rgb"),
        )
        for faction in factions
    ]

    def action(conn):
        conn.executemany(
            """
            INSERT INTO map_ledger_factions
                (map_id, faction_key, faction_id, founded_at,
                 first_seen_day, first_seen_at, last_seen_day, last_seen_at,
                 last_name, last_rgb)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(map_id, faction_key) DO UPDATE SET
                first_seen_day = MIN(first_seen_day, excluded.first_seen_day),
                first_seen_at = CASE
                    WHEN excluded.first_seen_day < first_seen_day
                    THEN excluded.first_seen_at ELSE first_seen_at END,
                last_seen_day = MAX(last_seen_day, excluded.last_seen_day),
                last_seen_at = CASE
                    WHEN excluded.last_seen_day >= last_seen_day
                    THEN excluded.last_seen_at ELSE last_seen_at END,
                last_name = excluded.last_name,
                last_rgb = excluded.last_rgb,
                deleted_day = NULL,
                deleted_at = NULL
            """,
            rows,
        )

    _write(conn, action)


_PRESENT_KEYS_TEMP = "_ledger_present_keys"


def mark_deleted(map_id: str, day: str, captured_at: str, present_keys, *, conn=None) -> int:
    """Mark every live faction absent from `day` as deleted on it.

    Caller must have checked `deletion_safe`: absence in a partial snapshot
    means the plugin ran out of budget, not that the faction was disbanded.
    Returns the number of rows marked.

    The present keys go into a TEMP table rather than an inlined `NOT IN (?, ?,
    …)`. `MAX_FACTIONS` is 2000 and SQLite's `SQLITE_MAX_VARIABLE_NUMBER` is 999
    on builds before 3.32 — so on exactly the busy server the cap was sized for,
    the inlined form raised, `_run_promote_ledger_day` swallowed it, and the day
    never indexed. A TEMP table costs one variable per row instead, and it is
    private to this connection, so a caller-supplied connection is safe too.
    """
    validate_map(map_id)
    if not is_valid_day(day):
        raise ValueError("Invalid ledger day")
    keys = list(present_keys)

    def action(conn):
        # `last_seen_day <= day` guards a backfill: re-promoting an old day
        # must not bury a faction that is alive in later days.
        sql = (
            "UPDATE map_ledger_factions SET deleted_day = ?, deleted_at = ? "
            "WHERE map_id = ? AND deleted_day IS NULL AND last_seen_day <= ?"
        )
        params: list = [day, captured_at, map_id, day]
        if not keys:
            return conn.execute(sql, params).rowcount

        conn.execute(f"DROP TABLE IF EXISTS temp.{_PRESENT_KEYS_TEMP}")
        conn.execute(
            f"CREATE TEMP TABLE {_PRESENT_KEYS_TEMP} (faction_key TEXT PRIMARY KEY)"
        )
        try:
            conn.executemany(
                f"INSERT OR IGNORE INTO {_PRESENT_KEYS_TEMP} (faction_key) VALUES (?)",
                [(key,) for key in keys],
            )
            sql += (
                " AND faction_key NOT IN "
                f"(SELECT faction_key FROM {_PRESENT_KEYS_TEMP})"
            )
            return conn.execute(sql, params).rowcount
        finally:
            conn.execute(f"DROP TABLE IF EXISTS temp.{_PRESENT_KEYS_TEMP}")

    return _write(conn, action)


def delete_day(map_id: str, day: str) -> None:
    """Drop every indexed row for one day. Used by reindex before a rebuild."""
    validate_map(map_id)
    if not is_valid_day(day):
        raise ValueError("Invalid ledger day")
    conn = connect()
    try:
        with conn:
            for table in (
                "map_ledger_faction_days",
                "map_ledger_guild_days",
                "map_ledger_days",
            ):
                conn.execute(
                    f"DELETE FROM {table} WHERE map_id = ? AND day = ?", (map_id, day)
                )
    finally:
        conn.close()


# --- reads -------------------------------------------------------------------


def _day_dict(row) -> dict:
    out = {column: row[column] for column in _DAY_COLUMNS}
    out["complete"] = bool(out["complete"])
    return out


def list_days(map_id: str) -> list[dict]:
    """Every indexed day, oldest first — one connect, one ordered SELECT.

    `globals` is deliberately not selected: the index route only needs the
    per-day metadata, and the globals blob is the bulk of the row.
    """
    validate_map(map_id)
    conn = connect()
    try:
        rows = conn.execute(
            f"SELECT {', '.join(_quote(c) for c in _DAY_COLUMNS)} "
            "FROM map_ledger_days WHERE map_id = ? ORDER BY day ASC",
            (map_id,),
        ).fetchall()
    finally:
        conn.close()
    return [_day_dict(row) for row in rows]


def latest_complete_day(map_id: str) -> str | None:
    validate_map(map_id)
    conn = connect()
    try:
        row = conn.execute(
            "SELECT day FROM map_ledger_days WHERE map_id = ? AND complete = 1 "
            "ORDER BY day DESC LIMIT 1",
            (map_id,),
        ).fetchone()
        return row["day"] if row else None
    finally:
        conn.close()


def get_day(map_id: str, day: str) -> dict | None:
    """One day's metadata plus its parsed `global` block."""
    validate_map(map_id)
    if not is_valid_day(day):
        return None
    conn = connect()
    try:
        row = conn.execute(
            f"SELECT {', '.join(_quote(c) for c in _DAY_COLUMNS)}, globals "
            "FROM map_ledger_days WHERE map_id = ? AND day = ?",
            (map_id, day),
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        return None
    out = _day_dict(row)
    try:
        globals_blob = json.loads(row["globals"])
    except (TypeError, ValueError):
        globals_blob = {}
    # A blob that parses to a list would reach callers as `["field"]` ->
    # TypeError on a read route; degrade to empty like the chronicle manifests.
    out["global"] = globals_blob if isinstance(globals_blob, dict) else {}
    return out


def list_registry(map_id: str) -> list[dict]:
    """The faction registry, first-seen order. One connect, one ordered SELECT."""
    validate_map(map_id)
    conn = connect()
    try:
        rows = conn.execute(
            f"SELECT {', '.join(_quote(c) for c in _REGISTRY_COLUMNS)} "
            "FROM map_ledger_factions WHERE map_id = ? "
            "ORDER BY first_seen_day ASC, faction_id ASC",
            (map_id,),
        ).fetchall()
    finally:
        conn.close()
    return [{column: row[column] for column in _REGISTRY_COLUMNS} for row in rows]


def read_global_days(map_id: str, start: str, end: str) -> list[dict]:
    """Per-day metadata + globals across an inclusive day range, oldest first.

    One ordered SELECT for the whole range. The chronicle index route used to
    issue one query per day and each of those is a fresh sqlite3.connect plus
    its PRAGMA, so the cost scaled with the length of history — two years of
    captures meant 730 connections before the ETag was even computed. See the
    `chronicle.store.list_day_manifests` docstring; do not reintroduce it here,
    where the range read is the hot path rather than the index.
    """
    validate_map(map_id)
    if not is_valid_day(start) or not is_valid_day(end):
        raise ValueError("Invalid ledger day")
    conn = connect()
    try:
        rows = conn.execute(
            f"SELECT {', '.join(_quote(c) for c in _DAY_COLUMNS)}, globals "
            "FROM map_ledger_days WHERE map_id = ? AND day >= ? AND day <= ? "
            "ORDER BY day ASC",
            (map_id, start, end),
        ).fetchall()
    finally:
        conn.close()

    out: list[dict] = []
    for row in rows:
        entry = _day_dict(row)
        try:
            blob = json.loads(row["globals"])
        except (TypeError, ValueError):
            blob = {}
        entry["global"] = blob if isinstance(blob, dict) else {}
        out.append(entry)
    return out


def read_faction_days(
    map_id: str,
    start: str,
    end: str,
    faction_keys=None,
    *,
    full: bool = False,
) -> list[dict]:
    """Faction rows across an inclusive day range, ordered by (key, day).

    One connect, one ordered SELECT for the *whole* range and *every* requested
    key — never a query per day and never a query per faction. `full` adds the
    JSON columns (breakdowns, subjects, wars), which are most of the payload
    size; the columnar `fields=core` read must not pay for them.
    """
    validate_map(map_id)
    if not is_valid_day(start) or not is_valid_day(end):
        raise ValueError("Invalid ledger day")

    columns = ("day", *FACTION_DAY_COLUMNS)
    if full:
        columns = (*columns, *_FACTION_DAY_JSON_COLUMNS)

    sql = (
        f"SELECT {', '.join(_quote(c) for c in columns)} "
        "FROM map_ledger_faction_days "
        "WHERE map_id = ? AND day >= ? AND day <= ?"
    )
    params: list = [map_id, start, end]
    if faction_keys is not None:
        keys = list(faction_keys)
        if not keys:
            return []
        sql += f" AND faction_key IN ({', '.join('?' * len(keys))})"
        params.extend(keys)
    sql += " ORDER BY faction_key ASC, day ASC"

    conn = connect()
    try:
        rows = conn.execute(sql, params).fetchall()
    finally:
        conn.close()

    out: list[dict] = []
    for row in rows:
        entry = {column: row[column] for column in columns}
        for column in _FACTION_DAY_JSON_COLUMNS if full else ():
            try:
                entry[column] = json.loads(row[column])
            except (TypeError, ValueError):
                entry[column] = _empty_for(column)
        out.append(entry)
    return out


def count_factions_in_range(map_id: str, start: str, end: str) -> int:
    """How many distinct factions actually have rows in an inclusive range.

    The registry is *cumulative* — it keeps every faction the map ever held,
    deleted ones included — so it is the wrong denominator for "did the default
    selection leave anything out?". A mature map's registry outnumbers its live
    factions permanently, which made `truncated` true on every default request.
    """
    validate_map(map_id)
    if not is_valid_day(start) or not is_valid_day(end):
        raise ValueError("Invalid ledger day")
    conn = connect()
    try:
        row = conn.execute(
            "SELECT COUNT(DISTINCT faction_key) AS total FROM map_ledger_faction_days "
            "WHERE map_id = ? AND day >= ? AND day <= ?",
            (map_id, start, end),
        ).fetchone()
    finally:
        conn.close()
    return int(row["total"]) if row else 0


def faction_has_any_row(map_id: str, faction_key: str) -> bool:
    """Does this key appear anywhere in the map's history?

    `SELECT 1 … LIMIT 1` on the `(map_id, faction_key, day)` index: the caller
    only wants to tell "unknown key" from "known key, no rows in this window",
    and materialising a faction's whole history to answer that would sidestep
    every range cap the route enforces.
    """
    validate_map(map_id)
    conn = connect()
    try:
        row = conn.execute(
            "SELECT 1 FROM map_ledger_faction_days "
            "WHERE map_id = ? AND faction_key = ? LIMIT 1",
            (map_id, faction_key),
        ).fetchone()
    finally:
        conn.close()
    return row is not None
