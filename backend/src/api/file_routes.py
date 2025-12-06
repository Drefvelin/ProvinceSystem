from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

file_router = APIRouter()

# FIXED PATHS (go up two folders, not one)
BASE_DIR = os.path.dirname(__file__)                     # backend/src/api
OUTPUT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "output"))

MAP_DIR = os.path.join(OUTPUT_DIR, "maps")
REGION_DIR = os.path.join(OUTPUT_DIR, "regions")
BANNER_DIR = os.path.join(OUTPUT_DIR, "banner")

from fastapi.responses import FileResponse, Response

def add_cors(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response


@file_router.get("/mapdata/{map_type}")
async def get_map_file(map_type: str):
    file_path = os.path.join(MAP_DIR, f"{map_type}_map.png")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Map not found: {file_path}")

    return add_cors(FileResponse(file_path, media_type="image/png"))


@file_router.get("/regions/{map_type}/{file_name}")
async def get_region_file(map_type: str, file_name: str):
    folder = os.path.join(REGION_DIR, map_type)
    file_path = os.path.join(folder, file_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Region overlay not found: {file_path}")

    return add_cors(FileResponse(file_path, media_type="image/png"))


@file_router.get("/banners/{map_type}/{file_name}")
async def get_banner_file(map_type: str, file_name: str):
    folder = os.path.join(BANNER_DIR, map_type)
    file_path = os.path.join(folder, file_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Banner not found: {file_path}")

    return add_cors(FileResponse(file_path, media_type="image/png"))
