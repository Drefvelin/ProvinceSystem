from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
import os
from pathlib import Path

from ..scripts.util.dirs import (
    map_image,
    region_image,
    banner_image
)

ROUTER_DIR = Path(__file__).resolve().parent
OUTPUT_BASE = ROUTER_DIR.parent / "output"

file_router = APIRouter()

def add_cors(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response


@file_router.get("/{map_name}/mapdata/{map_type}")
async def get_map_file(map_name: str, map_type: str):
    file_path = map_image(map_name, map_type)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Map not found")

    return add_cors(FileResponse(file_path, media_type="image/png"))


@file_router.get("/{map_name}/regions/{map_type}/{file_name}")
async def get_region_file(map_name: str, map_type: str, file_name: str):
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

    return FileResponse(file_path, media_type="image/png")


@file_router.get("/{map_name}/banners/{mode}/{file_name}")
async def get_banner_file(map_name: str, mode: str, file_name: str):
    file_path = banner_image(map_name, mode, file_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Banner not found")

    return add_cors(FileResponse(file_path, media_type="image/png"))
