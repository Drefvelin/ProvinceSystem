from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import os
import json

router = APIRouter()

INPUTS_DIR = os.path.join(os.path.dirname(__file__), "..", "input")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "defines")

@router.get("/data/{map_type}")
async def get_map(map_type: str):
    filename = f"{map_type}.json"
    file_path = os.path.join(DATA_DIR, filename)

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)  # Load JSON content
        return JSONResponse(content=data)  # Return JSON directly

    return JSONResponse(content={"error": "Data not found"}, status_code=404)

@router.post("/data/upload/nation")
async def upload_nation_data(request: Request):
    try:
        data = await request.json()  # Parse incoming JSON
        target_path = os.path.join(INPUTS_DIR, "nation.json")

        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return JSONResponse(content={"message": "Nation data saved successfully."}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)