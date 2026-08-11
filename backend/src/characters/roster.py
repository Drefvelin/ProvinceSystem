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


def catalog_default_max_alive(slot_limits: dict[str, Any] | None = None) -> int:
    """Fallback max from creation catalog defaults ∩ hard_cap."""
    limits = slot_limits if isinstance(slot_limits, dict) else {}
    defaults = limits.get("defaults") if isinstance(limits.get("defaults"), dict) else {}
    try:
        default_max = int(defaults.get("max_alive_characters") or 3)
    except (TypeError, ValueError):
        default_max = 3
    try:
        hard_cap = int(limits.get("hard_cap") or 10)
    except (TypeError, ValueError):
        hard_cap = 10
    return max(1, min(default_max, hard_cap))


def get_player_meta(player_uuid: str) -> dict[str, Any]:
    """Return stored meta flags for a player (defaults if no row)."""
    from src.skins.db import connect

    uuid = (player_uuid or "").strip()
    empty = {
        "max_alive_characters": None,
        "eighteen": None,
        "real_age_set": False,
        "account_created_at_epoch": None,
        "name_colour_stops": 0,
    }
    if not uuid:
        return empty
    with connect() as conn:
        row = conn.execute(
            """
            SELECT max_alive_characters, eighteen, real_age_set,
                   account_created_at_epoch, name_colour_stops
            FROM character_player_meta
            WHERE player_uuid = ?
            """,
            (uuid,),
        ).fetchone()
    if row is None:
        return empty
    max_alive = None
    if row["max_alive_characters"] is not None:
        try:
            max_alive = max(1, int(row["max_alive_characters"]))
        except (TypeError, ValueError):
            max_alive = None
    eighteen = None
    if row["eighteen"] is not None:
        eighteen = bool(int(row["eighteen"]))
    real_age_set = bool(int(row["real_age_set"] or 0))
    account_created_at_epoch = None
    if row["account_created_at_epoch"] is not None:
        try:
            account_created_at_epoch = int(row["account_created_at_epoch"])
        except (TypeError, ValueError):
            account_created_at_epoch = None
        if account_created_at_epoch is not None and account_created_at_epoch <= 0:
            account_created_at_epoch = None
    name_colour_stops = 0
    if row["name_colour_stops"] is not None:
        try:
            name_colour_stops = max(0, int(row["name_colour_stops"]))
        except (TypeError, ValueError):
            name_colour_stops = 0
    return {
        "max_alive_characters": max_alive,
        "eighteen": eighteen,
        "real_age_set": real_age_set,
        "account_created_at_epoch": account_created_at_epoch,
        "name_colour_stops": name_colour_stops,
    }


def get_stored_max_alive(player_uuid: str) -> int | None:
    return get_player_meta(player_uuid)["max_alive_characters"]


def get_name_colour_stops(player_uuid: str) -> int:
    """Resolved colour-stop entitlement (0 = no colour)."""
    return int(get_player_meta(player_uuid).get("name_colour_stops") or 0)


def get_max_alive(
    player_uuid: str,
    slot_limits: dict[str, Any] | None = None,
) -> int:
    """Player entitlement if synced, else catalog default ∩ hard_cap."""
    stored = get_stored_max_alive(player_uuid)
    if stored is not None:
        return stored
    return catalog_default_max_alive(slot_limits)


def is_real_age_set(player_uuid: str) -> bool:
    return bool(get_player_meta(player_uuid)["real_age_set"])


def set_real_age(player_uuid: str, eighteen: bool) -> dict[str, Any]:
    """Persist 18+ attestation (player-level, once)."""
    from src.skins.db import connect

    uuid = (player_uuid or "").strip()
    if not uuid:
        raise RosterError("player_uuid is required")
    now = _iso_now()
    eighteen_int = 1 if eighteen else 0
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO character_player_meta (
                player_uuid, max_alive_characters, eighteen, real_age_set, updated_at
            )
            VALUES (?, NULL, ?, 1, ?)
            ON CONFLICT(player_uuid) DO UPDATE SET
                eighteen = excluded.eighteen,
                real_age_set = 1,
                updated_at = excluded.updated_at
            """,
            (uuid, eighteen_int, now),
        )
        conn.commit()
    return {
        "player_uuid": uuid,
        "eighteen": eighteen,
        "real_age_set": True,
    }


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


def replace_roster(
    player_uuid: str,
    characters: list,
    max_alive_characters: int | None = None,
    eighteen: bool | None = None,
    real_age_set: bool | None = None,
    account_created_at_epoch: int | None = None,
    name_colour_stops: int | None = None,
) -> dict[str, Any]:
    from src.skins.db import connect

    uuid = (player_uuid or "").strip()
    if not uuid:
        raise RosterError("player_uuid is required")
    if not isinstance(characters, list):
        raise RosterError("characters must be a list")

    max_alive: int | None = None
    if max_alive_characters is not None:
        try:
            max_alive = int(max_alive_characters)
        except (TypeError, ValueError) as e:
            raise RosterError("max_alive_characters must be an integer") from e
        if max_alive < 1:
            raise RosterError("max_alive_characters must be >= 1")

    if real_age_set is not None and not isinstance(real_age_set, bool):
        raise RosterError("real_age_set must be a boolean")
    if eighteen is not None and not isinstance(eighteen, bool):
        raise RosterError("eighteen must be a boolean")
    # Answering eighteen implies attestation completed.
    if eighteen is not None and real_age_set is None:
        real_age_set = True

    next_account_epoch: int | None = None
    if account_created_at_epoch is not None:
        try:
            next_account_epoch = int(account_created_at_epoch)
        except (TypeError, ValueError) as e:
            raise RosterError(
                "account_created_at_epoch must be an integer"
            ) from e
        if next_account_epoch <= 0:
            raise RosterError("account_created_at_epoch must be > 0")

    next_colour_stops: int | None = None
    if name_colour_stops is not None:
        try:
            next_colour_stops = int(name_colour_stops)
        except (TypeError, ValueError) as e:
            raise RosterError("name_colour_stops must be an integer") from e
        if next_colour_stops < 0:
            raise RosterError("name_colour_stops must be >= 0")

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
        if (
            max_alive is not None
            or eighteen is not None
            or real_age_set is not None
            or next_account_epoch is not None
            or next_colour_stops is not None
        ):
            existing = conn.execute(
                "SELECT * FROM character_player_meta WHERE player_uuid = ?",
                (uuid,),
            ).fetchone()
            next_max = max_alive
            next_eighteen = None if eighteen is None else (1 if eighteen else 0)
            next_real = None if real_age_set is None else (1 if real_age_set else 0)
            stored_epoch = next_account_epoch
            stored_stops = next_colour_stops
            if existing is not None:
                if next_max is None:
                    next_max = existing["max_alive_characters"]
                if next_eighteen is None:
                    next_eighteen = existing["eighteen"]
                if next_real is None:
                    next_real = int(existing["real_age_set"] or 0)
                if stored_epoch is None:
                    stored_epoch = existing["account_created_at_epoch"]
                if stored_stops is None:
                    try:
                        stored_stops = existing["name_colour_stops"]
                    except (KeyError, IndexError):
                        stored_stops = None
            else:
                if next_real is None:
                    next_real = 0
            conn.execute(
                """
                INSERT INTO character_player_meta (
                    player_uuid, max_alive_characters, eighteen, real_age_set,
                    account_created_at_epoch, name_colour_stops, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(player_uuid) DO UPDATE SET
                    max_alive_characters = excluded.max_alive_characters,
                    eighteen = excluded.eighteen,
                    real_age_set = excluded.real_age_set,
                    account_created_at_epoch = excluded.account_created_at_epoch,
                    name_colour_stops = excluded.name_colour_stops,
                    updated_at = excluded.updated_at
                """,
                (
                    uuid,
                    next_max,
                    next_eighteen,
                    next_real,
                    stored_epoch,
                    stored_stops,
                    now,
                ),
            )
        conn.commit()

    out: dict[str, Any] = {
        "ok": True,
        "player_uuid": uuid,
        "count": len(normalized),
    }
    if max_alive is not None:
        out["max_alive_characters"] = max_alive
    if eighteen is not None:
        out["eighteen"] = eighteen
    if real_age_set is not None:
        out["real_age_set"] = real_age_set
    if next_account_epoch is not None:
        out["account_created_at_epoch"] = next_account_epoch
    if next_colour_stops is not None:
        out["name_colour_stops"] = next_colour_stops
    return out
