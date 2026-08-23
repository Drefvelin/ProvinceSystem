"""Map viewer access control (public vs staff-only maps)."""

from __future__ import annotations

import os

from fastapi import HTTPException

from src.api.map_registry import MapEntry, get_map_entry, list_map_entries
from src.characters.rpc_player_meta import has_map_staff_access
from src.skins.codes import get_session

STAFF_MAP_FORBIDDEN_DETAIL = "Staff map access required"
STAFF_MAP_PERMISSION_DETAIL = "Staff map permission required"
EDITOR_STAFF_PERMISSION = "tfmc.map.staff"
UI_DEV_SESSION_TOKEN = "ui-dev-session"


def is_character_ui_dev() -> bool:
    return os.environ.get("CHARACTER_UI_DEV", "").strip() == "1"


def _is_ui_dev_session_token(token: str | None) -> bool:
    return bool(token) and token == UI_DEV_SESSION_TOKEN


def _ui_dev_staff_bypass(authorization: str | None) -> bool:
    if not is_character_ui_dev():
        return False
    return _is_ui_dev_session_token(parse_bearer(authorization))


def _ui_dev_character_session() -> dict:
    return {
        "scope": "character",
        "player_uuid": "ui-dev-player",
        "realm_id": "main",
    }


def parse_bearer(authorization: str | None) -> str | None:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    token = authorization[7:].strip()
    return token or None


def get_character_session(authorization: str | None) -> dict | None:
    token = parse_bearer(authorization)
    if not token:
        return None

    if is_character_ui_dev() and _is_ui_dev_session_token(token):
        return _ui_dev_character_session()

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

    if _ui_dev_staff_bypass(authorization):
        return entry

    session = get_character_session(authorization)
    if session is None:
        raise HTTPException(status_code=403, detail=STAFF_MAP_FORBIDDEN_DETAIL)

    if not _staff_map_allowed(session, entry):
        raise HTTPException(status_code=403, detail=STAFF_MAP_PERMISSION_DETAIL)

    return entry


def ensure_map_staff_write(map_name: str, authorization: str | None) -> MapEntry:
    """Require staff map permission to write title/editor data (any registry map)."""
    entry = get_map_entry(map_name)
    if entry is None:
        raise HTTPException(status_code=404, detail="Map not found")

    if _ui_dev_staff_bypass(authorization):
        return entry

    session = get_character_session(authorization)
    if session is None:
        raise HTTPException(status_code=403, detail=STAFF_MAP_FORBIDDEN_DETAIL)

    permission = (entry.staff_permission or "").strip() or EDITOR_STAFF_PERMISSION
    if not has_map_staff_access(
        str(session.get("player_uuid") or ""),
        _session_realm_id(session),
        permission,
    ):
        raise HTTPException(status_code=403, detail=STAFF_MAP_PERMISSION_DETAIL)

    return entry


def list_accessible_maps(authorization: str | None) -> list[MapEntry]:
    if _ui_dev_staff_bypass(authorization):
        return list_map_entries()

    session = get_character_session(authorization)

    accessible: list[MapEntry] = []
    for entry in list_map_entries():
        if entry.public:
            accessible.append(entry)
            continue
        if session and _staff_map_allowed(session, entry):
            accessible.append(entry)

    return accessible
