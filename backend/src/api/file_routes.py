from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import FileResponse
import os
from pathlib import Path

from .http_headers import add_cors, add_no_cache
from .map_access import ensure_map_access
from ..scripts.util.dirs import (
    map_image,
    region_image,
    banner_image,
    zoc_image,
    validate_map,
)
from ..scripts.util.zoc_paths import safe_fort_filename

ROUTER_DIR = Path(__file__).resolve().parent
OUTPUT_BASE = ROUTER_DIR.parent / "output"

file_router = APIRouter()


@file_router.get("/{map_name}/mapdata/{map_type}")
async def get_map_file(
    map_name: str,
    map_type: str,
    authorization: str | None = Header(default=None),
):
    ensure_map_access(map_name, authorization)
    file_path = (
        OUTPUT_BASE
        / map_name
        / "maps"
        / f"{map_type}_map.png"
    )

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Map not found")

    return add_no_cache(add_cors(FileResponse(file_path, media_type="image/png")))


@file_router.get("/{map_name}/regions/{map_type}/{file_name}")
async def get_region_file(
    map_name: str,
    map_type: str,
    file_name: str,
    authorization: str | None = Header(default=None),
):
    ensure_map_access(map_name, authorization)
    # Ensure .png extension
    if not file_name.endswith(".png"):
        file_name = f"{file_name}.png"

    file_path = (
        OUTPUT_BASE
        / map_name
        / "regions"
        / map_type
        / file_name
    )

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Region overlay not found")

    return add_no_cache(add_cors(FileResponse(file_path, media_type="image/png")))


@file_router.get("/{map_name}/banners/{mode}/{file_name}")
async def get_banner_file(
    map_name: str,
    mode: str,
    file_name: str,
    authorization: str | None = Header(default=None),
):
    ensure_map_access(map_name, authorization)
    file_path = banner_image(map_name, mode, file_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Banner not found")

    return add_no_cache(add_cors(FileResponse(file_path, media_type="image/png")))


@file_router.get("/{map_name}/zoc/{fort_id}")
async def get_zoc_overlay(
    map_name: str,
    fort_id: str,
    authorization: str | None = Header(default=None),
):
    ensure_map_access(map_name, authorization)
    try:
        validate_map(map_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    fort_id = fort_id.strip()
    if fort_id.lower().endswith(".png"):
        fort_id = fort_id[:-4]
    safe_id = safe_fort_filename(fort_id)
    if safe_id is None:
        raise HTTPException(status_code=400, detail="Invalid fort id")

    file_path = Path(zoc_image(map_name, safe_id))
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="ZOC overlay not found")

    return add_no_cache(add_cors(FileResponse(file_path, media_type="image/png")))
