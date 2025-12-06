from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import os
import time

map_router = APIRouter()

MAPS_DIR = os.path.join(os.path.dirname(__file__), "..", "output", "maps")
INPUTS_DIR = os.path.join(os.path.dirname(__file__), "..", "input")

from src.scripts.util.imagechecker import find_province

from fastapi.responses import FileResponse, Response

def add_cors(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response

@map_router.get("/map")
async def get_base_map():
    file_path = os.path.join(INPUTS_DIR, "map.png")
    return add_cors(FileResponse(file_path) if os.path.exists(file_path) else JSONResponse({"error": "Map not found"}, status_code=404))

@map_router.get("/map/province/{coords}")
async def get_province(coords: str):
    try:
        start = time.time()
        # 2. Parse coordinates
        x_str, z_str = coords.split(",")
        x, z = int(x_str), int(z_str)
        province_id = find_province(x, z)

        if province_id == 0:
            return JSONResponse(
                content={
                        "province_id": 0,
                    },
                status_code=404,
            )
        duration = time.time() - start
        print(f"Province lookup took {duration:.3f} seconds")
        return JSONResponse(
            content={
                "province_id": province_id,
            }
        )

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid coordinates format. Use x,z")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")