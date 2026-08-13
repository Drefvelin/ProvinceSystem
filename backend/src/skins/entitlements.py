"""ArmourShop skin-upload entitlements (colour stops + 3D pair byte budget)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.name_colours import MAX_NAME_COLOURS, effective_colour_cap

# Emergency BE fallback when catalog defaults were never synced (ops misconfig).
EMERGENCY_MAX_3D_PAIR_BYTES = 30720


class PlayerMetaError(ValueError):
    """Invalid player-meta payload."""


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _nonneg_int(raw: Any, field: str) -> int:
    try:
        value = int(raw)
    except (TypeError, ValueError) as e:
        raise PlayerMetaError(f"{field} must be an integer") from e
    if value < 0:
        raise PlayerMetaError(f"{field} must be >= 0")
    return value


def catalog_entitlement_defaults(catalog: dict[str, Any] | None) -> dict[str, int]:
    """Read defaults from catalog.entitlements; may return empty ints if missing."""
    entitlements = (catalog or {}).get("entitlements")
    if not isinstance(entitlements, dict):
        return {"name_colour_stops": 0, "max_3d_pair_bytes": 0}
    defaults = entitlements.get("defaults")
    if not isinstance(defaults, dict):
        return {"name_colour_stops": 0, "max_3d_pair_bytes": 0}
    stops = defaults.get("name_colour_stops")
    pair = defaults.get("max_3d_pair_bytes")
    try:
        stops_i = max(0, int(stops))
    except (TypeError, ValueError):
        stops_i = 0
    try:
        pair_i = max(0, int(pair))
    except (TypeError, ValueError):
        pair_i = 0
    return {"name_colour_stops": stops_i, "max_3d_pair_bytes": pair_i}


def get_player_meta(player_uuid: str) -> dict[str, int] | None:
    from .db import connect

    uuid = (player_uuid or "").strip().lower()
    if not uuid:
        return None
    with connect() as conn:
        row = conn.execute(
            """
            SELECT name_colour_stops, max_3d_pair_bytes
            FROM armourshop_player_meta
            WHERE LOWER(player_uuid) = ?
            """,
            (uuid,),
        ).fetchone()
    if row is None:
        return None
    stops = 0
    pair = 0
    if row["name_colour_stops"] is not None:
        try:
            stops = max(0, int(row["name_colour_stops"]))
        except (TypeError, ValueError):
            stops = 0
    if row["max_3d_pair_bytes"] is not None:
        try:
            pair = max(0, int(row["max_3d_pair_bytes"]))
        except (TypeError, ValueError):
            pair = 0
    return {"name_colour_stops": stops, "max_3d_pair_bytes": pair}


def upsert_player_meta(raw: dict[str, Any]) -> dict[str, Any]:
    """Upsert ArmourShop player entitlements from plugin push."""
    from .db import connect

    if not isinstance(raw, dict):
        raise PlayerMetaError("body must be a JSON object")
    uuid = str(raw.get("player_uuid") or "").strip().lower()
    if not uuid:
        raise PlayerMetaError("player_uuid is required")
    stops = _nonneg_int(raw.get("name_colour_stops"), "name_colour_stops")
    pair = _nonneg_int(raw.get("max_3d_pair_bytes"), "max_3d_pair_bytes")
    updated_at = _iso_now()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO armourshop_player_meta (
                player_uuid, name_colour_stops, max_3d_pair_bytes, updated_at
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT(player_uuid) DO UPDATE SET
                name_colour_stops = excluded.name_colour_stops,
                max_3d_pair_bytes = excluded.max_3d_pair_bytes,
                updated_at = excluded.updated_at
            """,
            (uuid, stops, pair, updated_at),
        )
        conn.commit()
    return {
        "ok": True,
        "player_uuid": uuid,
        "name_colour_stops": stops,
        "max_3d_pair_bytes": pair,
        "updated_at": updated_at,
    }


def resolve_skin_entitlements(
    player_uuid: str,
    *,
    staff: bool = False,
) -> dict[str, int]:
    """
    Prefer armourshop_player_meta; else catalog defaults; else emergency pair bytes.
    Staff colour cap is MAX_NAME_COLOURS (8); 3D still uses meta/defaults.
    """
    from .catalog import get_catalog

    meta = get_player_meta(player_uuid)
    defaults = catalog_entitlement_defaults(get_catalog())

    if meta is not None:
        stops = meta["name_colour_stops"]
        pair = meta["max_3d_pair_bytes"]
    else:
        stops = defaults["name_colour_stops"]
        pair = defaults["max_3d_pair_bytes"]

    if pair <= 0:
        pair = EMERGENCY_MAX_3D_PAIR_BYTES

    if staff:
        colour_cap = MAX_NAME_COLOURS
    else:
        colour_cap = effective_colour_cap(stops)

    return {
        "name_colour_stops": colour_cap,
        "max_3d_pair_bytes": pair,
    }
