from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse
import os

router = APIRouter()

MAPS_DIR = os.path.join(os.path.dirname(__file__), "..", "output", "maps")
INPUTS_DIR = os.path.join(os.path.dirname(__file__), "..", "input")

@router.get("/map/{map_type}")
async def get_map(map_type: str):
    file_path = os.path.join(MAPS_DIR, f"{map_type}_map.png")
    return FileResponse(file_path) if os.path.exists(file_path) else JSONResponse({"error": "Map not found"}, status_code=404)

@router.get("/map")
async def get_base_map():
    file_path = os.path.join(INPUTS_DIR, "map.png")
    return FileResponse(file_path) if os.path.exists(file_path) else JSONResponse({"error": "Map not found"}, status_code=404)