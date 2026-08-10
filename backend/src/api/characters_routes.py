"""Characters API routes (catalog, session, create/list, plugin ingest)."""

from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field

from src.characters.creation_catalog import (
    CreationCatalogError,
    get_catalog,
    replace_catalog,
)
from src.characters.creates import (
    CreateError,
    create_character,
    list_for_player,
    list_pending,
    mark_applied_results,
)
from src.characters.roster import RosterError, replace_roster
from src.skins.auth import HEADER_PLUGIN_KEY, AuthError, require_plugin_key
from src.skins.codes import get_session, revoke_session

characters_router = APIRouter(prefix="/characters", tags=["characters"])


class AppliedResultsBody(BaseModel):
    results: list[dict] = Field(default_factory=list)


class RosterBody(BaseModel):
    player_uuid: str = Field(..., min_length=1)
    characters: list[dict] = Field(default_factory=list)
    max_alive_characters: int | None = None


def _require_plugin(x_plugin_key: str | None) -> None:
    try:
        require_plugin_key(x_plugin_key)
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


def _bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization Bearer token",
        )
    token = authorization[7:].strip()
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization Bearer token",
        )
    return token


def _character_session_from_auth(authorization: str | None) -> dict:
    token = _bearer_token(authorization)
    row = get_session(token)
    if row is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    scope = str(row.get("scope") or "").strip().lower()
    if scope != "character":
        raise HTTPException(
            status_code=401,
            detail="Character session required (scope=character)",
        )
    return row


@characters_router.put("/plugin/creation-catalog")
async def plugin_put_creation_catalog(
    request: Request,
    x_plugin_key: str | None = Header(default=None, alias=HEADER_PLUGIN_KEY),
):
    """RPCharacters full-replace creation catalog snapshot."""
    _require_plugin(x_plugin_key)
    try:
        body = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail="body must be JSON") from e
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="body must be a JSON object")
    try:
        result = replace_catalog(body)
    except CreationCatalogError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {
        "ok": True,
        "stages": result["stages_count"],
        "races": result["races_count"],
        "traits": result["traits_count"],
        "classes": result["classes_count"],
        "updated_at": result["updated_at"],
    }


@characters_router.get("/creation-catalog")
def get_creation_catalog(
    authorization: str | None = Header(default=None),
):
    """Session-gated creation catalog for the website wizard."""
    _character_session_from_auth(authorization)
    return get_catalog()


@characters_router.post("/logout")
def post_logout(
    authorization: str | None = Header(default=None),
):
    """Revoke the current Bearer session (idempotent)."""
    token = _bearer_token(authorization)
    return revoke_session(token)


@characters_router.post("")
@characters_router.post("/")
async def post_character(
    request: Request,
    authorization: str | None = Header(default=None),
):
    """Queue a web character create (validated against synced catalog)."""
    session = _character_session_from_auth(authorization)
    try:
        body = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail="body must be JSON") from e
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="body must be a JSON object")
    try:
        row = create_character(session["player_uuid"], body)
    except CreateError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {
        "ok": True,
        "id": row["id"],
        "status": row["status"],
        "client_request_id": row["client_request_id"],
        "created_at": row["created_at"],
        "payload": row["payload"],
    }


@characters_router.get("")
@characters_router.get("/")
def get_characters(
    authorization: str | None = Header(default=None),
):
    """List roster mirror + pending creates for the session player."""
    session = _character_session_from_auth(authorization)
    return list_for_player(session["player_uuid"])


@characters_router.get("/plugin/pending")
def plugin_pending_creates(
    x_plugin_key: str | None = Header(default=None, alias=HEADER_PLUGIN_KEY),
):
    _require_plugin(x_plugin_key)
    return {"creates": list_pending()}


@characters_router.post("/plugin/applied")
def plugin_applied_creates(
    body: AppliedResultsBody,
    x_plugin_key: str | None = Header(default=None, alias=HEADER_PLUGIN_KEY),
):
    _require_plugin(x_plugin_key)
    try:
        return mark_applied_results(body.results)
    except CreateError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@characters_router.put("/plugin/roster")
def plugin_put_roster(
    body: RosterBody,
    x_plugin_key: str | None = Header(default=None, alias=HEADER_PLUGIN_KEY),
):
    _require_plugin(x_plugin_key)
    try:
        return replace_roster(
            body.player_uuid,
            body.characters,
            body.max_alive_characters,
        )
    except RosterError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
