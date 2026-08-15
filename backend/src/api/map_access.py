"""Map viewer access control (public vs staff-only maps)."""

from __future__ import annotations

from fastapi import HTTPException

from src.api.map_registry import MapEntry, get_map_entry, list_map_entries
from src.characters.rpc_player_meta import has_map_staff_access
from src.skins.codes import get_session

STAFF_MAP_FORBIDDEN_DETAIL = "Staff map access required"
STAFF_MAP_PERMISSION_DETAIL = "Staff map permission required"


def parse_bearer(authorization: str | None) -> str | None:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    token = authorization[7:].strip()
    return token or None


def get_character_session(authorization: str | None) -> dict | None:
    token = parse_bearer(authorization)
    if not token:
        return None

    row = get_session(token)
    if row is None:
        return None

    scope = str(row.get("scope") or "").strip().lower()
    if scope != "character":
        return None

    return row


def _session_realm_id(session: dict) -> str:
    return str(session.get("realm_id") or "main").strip().lower() or "main"


def _staff_map_allowed(session: dict, map_entry: MapEntry) -> bool:
    permission = (map_entry.staff_permission or "").strip()
    if not permission:
        return False
    return has_map_staff_access(
        str(session.get("player_uuid") or ""),
        _session_realm_id(session),
        permission,
    )


def ensure_map_access(map_name: str, authorization: str | None) -> MapEntry:
    entry = get_map_entry(map_name)
    if entry is None:
        raise HTTPException(status_code=404, detail="Map not found")

    if entry.public:
        return entry

    session = get_character_session(authorization)
    if session is None:
        raise HTTPException(status_code=403, detail=STAFF_MAP_FORBIDDEN_DETAIL)

    if not _staff_map_allowed(session, entry):
        raise HTTPException(status_code=403, detail=STAFF_MAP_PERMISSION_DETAIL)

    return entry


def list_accessible_maps(authorization: str | None) -> list[MapEntry]:
    session = get_character_session(authorization)

    accessible: list[MapEntry] = []
    for entry in list_map_entries():
        if entry.public:
            accessible.append(entry)
            continue
        if session and _staff_map_allowed(session, entry):
            accessible.append(entry)

    return accessible
