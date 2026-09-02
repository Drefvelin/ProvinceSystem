from fastapi import APIRouter, Header, HTTPException
import os
from pathlib import Path

from .http_headers import conditional_file_response
from .map_access import ensure_map_access
from .webp_cache import webp_variant
from ..scripts.util.dirs import (
    map_image,
    region_image,
    banner_image,
    zoc_image,
    validate_map,
    input_file,
)
from ..scripts.util.zoc_paths import safe_fort_filename

ROUTER_DIR = Path(__file__).resolve().parent
OUTPUT_BASE = ROUTER_DIR.parent / "output"

file_router = APIRouter()


def _image_response(
    file_path,
    accept: str | None,
    if_none_match: str | None,
    if_modified_since: str | None,
):
    """Serve a display-only overlay, preferring a cached WebP copy.

    Same shape as `map_routes._base_map_response`: falls back to the PNG while
    no fresh WebP exists, so a request is never blocked on the encode.

    Only for images the browser merely draws. The `mapdata` pick maps are read
    back pixel-by-pixel to resolve region ids, so they stay raw PNG.
    """
    webp = webp_variant(file_path, accept=accept)
    served = str(webp) if webp else str(file_path)
    media_type = "image/webp" if webp else "image/png"

    response = conditional_file_response(
        served,
        media_type=media_type,
        if_none_match=if_none_match,
        if_modified_since=if_modified_since,
    )
    # The body depends on whether the client advertised WebP, so caches must key on it.
    response.headers["Vary"] = "Accept"
    return response


@file_router.get("/{map_name}/mapdata/{map_type}")
async def get_map_file(
    map_name: str,
    map_type: str,
    authorization: str | None = Header(default=None),
    if_none_match: str | None = Header(default=None),
    if_modified_since: str | None = Header(default=None),
):
    ensure_map_access(map_name, authorization)

    # The province mode paints the source pick map itself, so there is
    # nothing to generate and nothing for a regen to keep in sync.
    if map_type == "province":
        try:
            validate_map(map_name)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        file_path = Path(input_file(map_name, "provinces.png"))
    else:
        file_path = (
            OUTPUT_BASE
            / map_name
            / "maps"
            / f"{map_type}_map.png"
        )

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Map not found")

    # Deliberately NOT routed through webp_variant: this is the pick map. The
    # client draws it to an offscreen canvas and reads exact RGB values back to
    # resolve province/county ids, and lossy WebP would corrupt those lookups.
    return conditional_file_response(
        file_path,
        media_type="image/png",
        if_none_match=if_none_match,
        if_modified_since=if_modified_since,
    )


@file_router.get("/{map_name}/regions/{map_type}/{file_name}")
async def get_region_file(
    map_name: str,
    map_type: str,
    file_name: str,
    authorization: str | None = Header(default=None),
    accept: str | None = Header(default=None),
    if_none_match: str | None = Header(default=None),
    if_modified_since: str | None = Header(default=None),
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

    return _image_response(file_path, accept, if_none_match, if_modified_since)


@file_router.get("/{map_name}/banners/{mode}/{file_name}")
async def get_banner_file(
    map_name: str,
    mode: str,
    file_name: str,
    authorization: str | None = Header(default=None),
    accept: str | None = Header(default=None),
    if_none_match: str | None = Header(default=None),
    if_modified_since: str | None = Header(default=None),
):
    ensure_map_access(map_name, authorization)
    file_path = banner_image(map_name, mode, file_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Banner not found")

    return _image_response(file_path, accept, if_none_match, if_modified_since)


@file_router.get("/{map_name}/zoc/{fort_id}")
async def get_zoc_overlay(
    map_name: str,
    fort_id: str,
    authorization: str | None = Header(default=None),
    accept: str | None = Header(default=None),
    if_none_match: str | None = Header(default=None),
    if_modified_since: str | None = Header(default=None),
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

    return _image_response(file_path, accept, if_none_match, if_modified_since)
