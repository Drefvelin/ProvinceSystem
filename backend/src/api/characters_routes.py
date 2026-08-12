"""Characters API routes (catalog, session, create/list, plugin ingest)."""

from __future__ import annotations

import json

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
from src.characters.lore_items import (
    LoreItemError,
    claim_status,
    customise_lore_item,
    list_character_kits,
    list_lore_items,
    list_pending_for_plugin,
    mark_lore_items_applied,
    resolve_pickable_texture,
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
    eighteen: bool | None = None
    real_age_set: bool | None = None
    account_created_at_epoch: int | None = None
    name_colour_stops: int | None = None
    kit_cooldown_seconds_remaining: int | None = None
    kit_cooldown_hours: int | None = None
    kit_cooldowns: dict | None = None


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


def _lore_http(exc: LoreItemError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=str(exc))


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


@characters_router.get("/kits")
def get_character_kits(
    character_id: str | None = None,
    authorization: str | None = Header(default=None),
):
    """All kits + items + claimability for a roster character."""
    session = _character_session_from_auth(authorization)
    try:
        return list_character_kits(session["player_uuid"], character_id)
    except LoreItemError as e:
        raise _lore_http(e) from e


@characters_router.get("/lore-items")
def get_lore_items(
    character_id: str | None = None,
    kit_id: str | None = None,
    authorization: str | None = Header(default=None),
):
    """Editable kit parts + customise drafts for a claimable kit."""
    session = _character_session_from_auth(authorization)
    try:
        return list_lore_items(session["player_uuid"], character_id, kit_id)
    except LoreItemError as e:
        raise _lore_http(e) from e


@characters_router.get("/lore-items/skins/{submission_id}/texture")
def get_lore_item_skin_texture(
    submission_id: str,
    base_set: str | None = None,
    authorization: str | None = Header(default=None),
):
    """PNG preview for a pickable skin (own applied or staff i_tools)."""
    from fastapi.responses import FileResponse

    session = _character_session_from_auth(authorization)
    try:
        path = resolve_pickable_texture(
            session["player_uuid"], submission_id, base_set
        )
    except LoreItemError as e:
        raise _lore_http(e) from e
    return FileResponse(
        path,
        media_type="image/png",
        filename=f"{submission_id}.png",
    )


@characters_router.post("/lore-items/{kit_key}/customise")
async def post_lore_item_customise(
    kit_key: str,
    request: Request,
    character_id: str | None = None,
    kit_id: str | None = None,
    authorization: str | None = Header(default=None),
):
    """Store name/lore draft; optional existing skin or new handheld PNG upload."""
    session = _character_session_from_auth(authorization)
    content_type = (request.headers.get("content-type") or "").lower()

    display_name: str | None = None
    lore: list[str] | None = None
    existing_skin_id = None
    existing_provided = False
    texture_bytes: bytes | None = None
    model_bytes: bytes | None = None
    use_3d = False
    name_colours: list[str] | None = None

    if "multipart/form-data" in content_type:
        form = await request.form()
        display_name = str(form.get("display_name") or "")
        lore_raw = form.get("lore")
        if lore_raw is not None and str(lore_raw).strip() != "":
            try:
                parsed = json.loads(str(lore_raw))
                if not isinstance(parsed, list):
                    raise ValueError("not a list")
                lore = [str(x) for x in parsed]
            except Exception as e:
                raise HTTPException(
                    status_code=400, detail="lore must be a JSON array"
                ) from e
        else:
            lore = []
        if "existing_skin_id" in form:
            existing_provided = True
            raw_skin = form.get("existing_skin_id")
            if raw_skin is None or str(raw_skin).strip() == "":
                existing_skin_id = None
            else:
                existing_skin_id = str(raw_skin).strip()
        texture = form.get("texture")
        if texture is not None and hasattr(texture, "read"):
            texture_bytes = await texture.read()
        model = form.get("model")
        if model is not None and hasattr(model, "read"):
            model_bytes = await model.read()
        use_3d = str(form.get("use_3d") or "").strip().lower() in (
            "1",
            "true",
            "yes",
        )
        colours_raw = form.get("name_colours")
        if colours_raw is not None and str(colours_raw).strip() != "":
            try:
                parsed_c = json.loads(str(colours_raw))
                if not isinstance(parsed_c, list):
                    raise ValueError("not a list")
                name_colours = [str(x) for x in parsed_c]
            except Exception as e:
                raise HTTPException(
                    status_code=400, detail="name_colours must be a JSON array"
                ) from e
    else:
        try:
            body = await request.json()
        except Exception as e:
            raise HTTPException(status_code=400, detail="body must be JSON") from e
        if not isinstance(body, dict):
            raise HTTPException(status_code=400, detail="body must be a JSON object")
        display_name = str(body.get("display_name") or "")
        lore_raw = body.get("lore")
        if lore_raw is None:
            lore = []
        elif isinstance(lore_raw, list):
            lore = [str(x) for x in lore_raw]
        else:
            raise HTTPException(status_code=400, detail="lore must be a list")
        if "existing_skin_id" in body:
            existing_provided = True
            existing_skin_id = body.get("existing_skin_id")
        use_3d = bool(body.get("use_3d"))
        colours_body = body.get("name_colours")
        if isinstance(colours_body, list):
            name_colours = [str(x) for x in colours_body]

    try:
        kwargs = dict(
            display_name=display_name,
            lore=lore,
            texture_bytes=texture_bytes,
            model_bytes=model_bytes,
            use_3d=use_3d,
            name_colours=name_colours,
            kit_id=kit_id,
        )
        if existing_provided:
            return customise_lore_item(
                session,
                character_id,
                kit_key,
                existing_skin_id=existing_skin_id,
                **kwargs,
            )
        return customise_lore_item(
            session,
            character_id,
            kit_key,
            **kwargs,
        )
    except LoreItemError as e:
        raise _lore_http(e) from e


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


@characters_router.get("/plugin/lore-items/pending")
def plugin_pending_lore_items(
    x_plugin_key: str | None = Header(default=None, alias=HEADER_PLUGIN_KEY),
):
    _require_plugin(x_plugin_key)
    return {"items": list_pending_for_plugin()}


@characters_router.get("/plugin/lore-items/claim-status")
def plugin_lore_item_claim_status(
    player_uuid: str | None = None,
    character_id: str | None = None,
    kit_id: str | None = None,
    x_plugin_key: str | None = Header(default=None, alias=HEADER_PLUGIN_KEY),
):
    """Whether kit claim should wait on pending_skin for this character/kit."""
    _require_plugin(x_plugin_key)
    uuid = (player_uuid or "").strip()
    cid = (character_id or "").strip()
    if not uuid or not cid:
        raise HTTPException(
            status_code=400, detail="player_uuid and character_id are required"
        )
    return claim_status(uuid, cid, kit_id)


class LoreItemsAppliedBody(BaseModel):
    results: list[dict] = Field(default_factory=list)


@characters_router.post("/plugin/lore-items/applied")
def plugin_applied_lore_items(
    body: LoreItemsAppliedBody,
    x_plugin_key: str | None = Header(default=None, alias=HEADER_PLUGIN_KEY),
):
    _require_plugin(x_plugin_key)
    try:
        return mark_lore_items_applied(body.results)
    except LoreItemError as e:
        raise _lore_http(e) from e


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
            body.eighteen,
            body.real_age_set,
            body.account_created_at_epoch,
            body.name_colour_stops,
            body.kit_cooldown_seconds_remaining,
            body.kit_cooldown_hours,
            body.kit_cooldowns,
        )
    except RosterError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
