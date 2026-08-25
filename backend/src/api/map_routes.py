from fastapi import APIRouter, Header, HTTPException, Response
from fastapi.responses import FileResponse, JSONResponse
import os, time

from .map_access import ensure_map_access
from ..scripts.util.dirs import input_file, parchment_image
from ..scripts.util.imagechecker import find_province

map_router = APIRouter()

# province_meta_cache.py
import time

_CACHE_TTL_SECONDS = 300  # 5 minutes

_PROVINCE_META_CACHE: dict[str, dict] = {}

def get_province_meta_cached(map_name: str) -> dict[int, dict]:
    now = time.time()

    entry = _PROVINCE_META_CACHE.get(map_name)

    if (
        entry is None or
        now - entry["loaded_at"] > _CACHE_TTL_SECONDS
    ):
        from ..scripts.loader.province_metadata import load_province_metadata
        _PROVINCE_META_CACHE[map_name] = {
            "data": load_province_metadata(map_name),
            "loaded_at": now,
        }

    return _PROVINCE_META_CACHE[map_name]["data"]

def add_cors(r: Response):
    r.headers["Access-Control-Allow-Origin"] = "*"
    r.headers["Access-Control-Allow-Headers"] = "*"
    r.headers["Access-Control-Allow-Methods"] = "*"
    return r

def add_no_cache(r: Response):
    r.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r

def _resolve_base_map_path(map_name: str, base: str) -> str | None:
    use_satellite = base.lower() in ("satellite", "colour", "color")
    if use_satellite:
        path = input_file(map_name, "map.png")
    else:
        parchment_path = parchment_image(map_name)
        path = (
            parchment_path
            if os.path.exists(parchment_path)
            else input_file(map_name, "map.png")
        )
    return path if os.path.exists(path) else None

@map_router.get("/{map_name}/map/parchment")
async def get_parchment_map(
    map_name: str,
    authorization: str | None = Header(default=None),
):
    ensure_map_access(map_name, authorization)
    path = _resolve_base_map_path(map_name, "parchment")
    if not path:
        return JSONResponse({"error": "Map not found"}, 404)
    r = FileResponse(path, media_type="image/png")
    r.headers["X-Map-Base"] = "parchment"
    return add_no_cache(add_cors(r))

@map_router.get("/{map_name}/map/original")
async def get_original_map(
    map_name: str,
    authorization: str | None = Header(default=None),
):
    return await get_base_map(map_name, authorization)

@map_router.get("/{map_name}/map")
async def get_base_map(
    map_name: str,
    authorization: str | None = Header(default=None),
):
    ensure_map_access(map_name, authorization)
    path = _resolve_base_map_path(map_name, "satellite")
    if not path:
        return JSONResponse({"error": "Map not found"}, 404)
    r = FileResponse(path, media_type="image/png")
    r.headers["X-Map-Base"] = "original"
    return add_no_cache(add_cors(r))

@map_router.get("/{map_name}/map/province/{coords}")
async def get_province(
    map_name: str,
    coords: str,
    authorization: str | None = Header(default=None),
):
    ensure_map_access(map_name, authorization)
    try:
        x, z = map(int, coords.split(","))
    except ValueError:
        raise HTTPException(400, "Invalid coordinates")

    t0 = time.time()
    pid = find_province(map_name, x, z)
    print(f"[{map_name}] province lookup {time.time() - t0:.3f}s")

    if pid == 0:
        return JSONResponse({"province_id": 0}, 404)
    return JSONResponse({"province_id": pid})

@map_router.get("/{map_name}/province/{coords}/meta")
async def get_province_meta(
    map_name: str,
    coords: str,
    authorization: str | None = Header(default=None),
):
    ensure_map_access(map_name, authorization)

    try:
        x, z = map(int, coords.split(","))
    except ValueError:
        raise HTTPException(400, "Invalid coordinates")

    pid = find_province(map_name, x, z)
    if pid == 0:
        return JSONResponse({"province_id": 0}, status_code=404)

    meta = get_province_meta_cached(map_name).get(pid)
    if not meta:
        return JSONResponse({"province_id": pid})

    return JSONResponse({
        "province_id": pid,
        "terrain": meta.get("terrain"),
        "fertility": meta.get("fertility"),
    })
