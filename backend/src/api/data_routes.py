import asyncio
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import os
import json

from src.scripts.util.task_lock import regen_lock
from src.scripts.util.regeneration import run_regeneration

import concurrent.futures


router = APIRouter()
executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)  # Optional: tune this if needed

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
        payload = await request.json()

        # Save nation.json
        target_path = os.path.join(INPUTS_DIR, "nation.json")
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        # Check for regeneration trigger
        if payload.get("regenerate"):
            mode = payload.get("mode", "nation")  # Default to nation
            regen_type = payload.get("regen_type", "queued")  # Optional: default to queued

            if regen_lock.locked():
                raise HTTPException(status_code=429, detail="Regeneration already in progress.")

            asyncio.create_task(run_regeneration(mode, regen_type))

            return JSONResponse(content={
                "message": "Nation data saved and regeneration started.",
                "regen_type": regen_type,
                "mode": mode
            }, status_code=200)

        return JSONResponse(content={"message": "Nation data saved successfully."}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
