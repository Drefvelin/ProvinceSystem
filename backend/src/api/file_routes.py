from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
import os

from ..scripts.util.dirs import (
    map_image,
    region_image,
    banner_image
)

file_router = APIRouter()

def add_cors(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response


@file_router.get("/{map}/mapdata/{map_type}")
async def get_map_file(map: str, map_type: str):
    file_path = map_image(map, map_type)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Map not found")

    return add_cors(FileResponse(file_path, media_type="image/png"))


@file_router.get("/{map}/regions/{type}/{file_name}")
async def get_region_file(map: str, type: str, file_name: str):
    file_path = region_image(map, type, file_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Region overlay not found")

    return add_cors(FileResponse(file_path, media_type="image/png"))


@file_router.get("/{map}/banners/{mode}/{file_name}")
async def get_banner_file(map: str, mode: str, file_name: str):
    file_path = banner_image(map, mode, file_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Banner not found")

    return add_cors(FileResponse(file_path, media_type="image/png"))
