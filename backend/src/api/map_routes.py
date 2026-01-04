from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse, JSONResponse
import os, time

from ..scripts.util.dirs import input_file, validate_map
from ..scripts.util.imagechecker import find_province

map_router = APIRouter()

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

@map_router.get("/{map_name}/map")
async def get_base_map(map_name: str):
    validate_map(map_name)
    path = input_file(map_name, "map.png")
    if not os.path.exists(path):
        return JSONResponse({"error": "Map not found"}, 404)
    r = FileResponse(path, media_type="image/png")
    return add_no_cache(add_cors(r))

@map_router.get("/{map_name}/map/province/{coords}")
async def get_province(map_name: str, coords: str):
    validate_map(map_name)
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
async def get_province_meta(map_name: str, coords: str):
    validate_map(map_name)
    try:
        x, z = map(int, coords.split(","))
    except ValueError:
        raise HTTPException(400, "Invalid coordinates")

    pid = find_province(map_name, x, z)
    if pid == 0:
        return JSONResponse({"province_id": 0}, 404)

    from ..scripts.loader.province_metadata import load_province_metadata
    meta = load_province_metadata(map_name).get(pid, {})
    return add_cors(JSONResponse({
        "province_id": pid,
        "terrain": meta.get("terrain"),
        "fertility": meta.get("fertility"),
    }))
