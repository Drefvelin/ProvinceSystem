from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse, JSONResponse
import os
import time

from ..scripts.util.dirs import (
    input_file,
    validate_map
)

from ..scripts.util.imagechecker import find_province

map_router = APIRouter()

def add_cors(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response

def add_no_cache(response: Response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@map_router.get("/{map}/map")
async def get_base_map(map: str):
    try:
        validate_map(map)

        file_path = input_file(map, "map.png")

        if not os.path.exists(file_path):
            return JSONResponse({"error": "Map not found"}, status_code=404)

        response = FileResponse(file_path, media_type="image/png")
        add_cors(response)
        add_no_cache(response)
        return response


    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@map_router.get("/{map}/map/province/{coords}")
async def get_province(map: str, coords: str):
    try:
        validate_map(map)

        # Parse coordinates
        x_str, z_str = coords.split(",")
        x, z = int(x_str), int(z_str)

        start = time.time()

        # IMPORTANT:
        # find_province MUST be map-aware internally
        province_id = find_province(map, x, z)

        duration = time.time() - start
        print(f"[{map}] Province lookup took {duration:.3f}s")

        if province_id == 0:
            return JSONResponse(
                content={"province_id": 0},
                status_code=404
            )

        return JSONResponse(content={"province_id": province_id})

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid coordinates format. Use x,z"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )

@map_router.get("/{map}/province/{coords}/meta")
async def get_province_meta(map: str, coords: str):
    try:
        validate_map(map)

        x_str, z_str = coords.split(",")
        x, z = int(x_str), int(z_str)

        province_id = find_province(map, x, z)

        if province_id == 0:
            return JSONResponse(
                content={"province_id": 0},
                status_code=404
            )

        # Load metadata (cached internally if possible)
        from ..scripts.loader.province_metadata import load_province_metadata
        meta = load_province_metadata(map).get(province_id, {})

        return JSONResponse(content={
            "province_id": province_id,
            "terrain": meta.get("terrain"),
            "fertility": meta.get("fertility"),
        })

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid coordinates")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))