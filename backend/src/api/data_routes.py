from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import json
import os

from ..scripts.util.dirs import (
    input_file,
    defines_file,
    validate_map
)

data_router = APIRouter()

@data_router.get("/{map}/data/{file}")
async def get_map_data(map: str, file: str):
    try:
        validate_map(map)

        file_path = defines_file(map, f"{file}.json")

        if not os.path.exists(file_path):
            return JSONResponse({"error": "Data not found"}, status_code=404)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return JSONResponse(content=data)

    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@data_router.post("/{map}/data/upload/{mode}")
async def upload_region_data(map: str, mode: str, request: Request):
    try:
        validate_map(map)

        payload = await request.json()

        if mode in {"nation", "queue"}:
            target_path = input_file(map, f"{mode}.json")
        else:
            target_path = defines_file(map, f"{mode}.json")

        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        return JSONResponse(
            {"message": f"{mode} data saved successfully for map '{map}'"},
            status_code=200
        )

    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
