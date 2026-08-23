"""Staff-gated map title editor API routes."""

from __future__ import annotations

import gzip
import json
import os

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, Response

from .data_routes import clear_province_cache
from .file_routes import add_cors
from .editor_validation import TITLE_TIERS, TitleValidationError, validate_title_tier
from .map_access import ensure_map_staff_write
from .regen_routes import _regen_start_message
from src.scripts.loader.provinces import load_province_catalog
from src.scripts.province_id_grid import (
    GRID_FILENAME,
    read_province_id_grid_file,
    serialize_province_id_grid,
)
from src.scripts.util.dirs import defines_file, input_file, validate_map
from src.scripts.util.regeneration import run_regeneration
from src.scripts.util.regen_types import parse_regen_type
from src.scripts.util.task_lock import get_map_lock

editor_router = APIRouter()


@editor_router.post("/{map_name}/editor/titles/{tier}")
async def save_title_tier(
    map_name: str,
    tier: str,
    request: Request,
    authorization: str | None = Header(default=None),
):
    ensure_map_staff_write(map_name, authorization)

    tier_norm = (tier or "").strip().lower()
    if tier_norm not in TITLE_TIERS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown title tier '{tier}'. Expected one of: {', '.join(sorted(TITLE_TIERS))}",
        )

    payload = await request.json()
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Title data must be a JSON object")

    try:
        clean = validate_title_tier(tier_norm, payload, map_name)
    except TitleValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    path = defines_file(map_name, f"{tier_norm}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(clean, handle, ensure_ascii=False, indent=2)

    clear_province_cache(map_name)

    return JSONResponse(
        {"ok": True, "tier": tier_norm, "count": len(clean)}
    )


@editor_router.post("/{map_name}/editor/regen/{regen_type}")
async def editor_regenerate(
    map_name: str,
    regen_type: str,
    background_tasks: BackgroundTasks,
    authorization: str | None = Header(default=None),
):
    ensure_map_staff_write(map_name, authorization)

    try:
        validate_map(map_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        parse_regen_type(regen_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    map_lock = get_map_lock(map_name)
    if map_lock.locked():
        raise HTTPException(
            status_code=429,
            detail=f"Regeneration already in progress for map '{map_name}'.",
        )

    background_tasks.add_task(run_regeneration, map_name, regen_type)

    return JSONResponse(
        {
            "ok": True,
            "regen_type": regen_type,
            "message": _regen_start_message(regen_type),
        }
    )


@editor_router.get("/{map_name}/editor/provinces")
async def get_editor_provinces(
    map_name: str,
    authorization: str | None = Header(default=None),
):
    ensure_map_staff_write(map_name, authorization)

    try:
        provinces = load_province_catalog(map_name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return JSONResponse({"provinces": provinces})


@editor_router.get("/{map_name}/editor/pick/provinces")
async def get_editor_province_pick(
    map_name: str,
    authorization: str | None = Header(default=None),
):
    """Staff-only raw provinces.png for editor province RGB hit-testing."""
    ensure_map_staff_write(map_name, authorization)

    try:
        validate_map(map_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    path = input_file(map_name, "provinces.png")
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Province pick map not found")

    return add_cors(FileResponse(path, media_type="image/png"))


@editor_router.get("/{map_name}/editor/province-index")
async def get_editor_province_index(
    map_name: str,
    authorization: str | None = Header(default=None),
):
    """Staff-only province id grid for editor hit-testing (gzip province_id_grid bytes)."""
    ensure_map_staff_write(map_name, authorization)

    try:
        validate_map(map_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    grid_path = defines_file(map_name, GRID_FILENAME)
    if not os.path.isfile(grid_path):
        raise HTTPException(
            status_code=404,
            detail=(
                f"Province grid not found for map '{map_name}'. "
                f"Run: python -m scripts.tools.build_province_id_grid --map {map_name}"
            ),
        )

    width, height, ids = read_province_id_grid_file(grid_path)

    payload = serialize_province_id_grid(width, height, ids)
    body = gzip.compress(payload)
    return add_cors(
        Response(content=body, media_type="application/octet-stream")
    )
