from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
import json
import os

from ..scripts.util.auth import HASHED_KEY
from ..scripts.util.queue import raw_queue_path

claim_router = APIRouter()

@claim_router.post("/{map}/{hashed_key}/api/queue/upload")
async def upload_queue(map: str, hashed_key: str, request: Request):
    # 1. Validate hash
    if hashed_key != HASHED_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 2. Basic map name safety (prevents path traversal)
    if not map.isalnum():
        raise HTTPException(status_code=400, detail="Invalid map name")

    try:
        # 3. Parse full JSON queue
        payload = await request.json()

        if not isinstance(payload, dict):
            raise HTTPException(status_code=400, detail="Payload must be a JSON object")

        # 4. Resolve map-specific queue path
        queue_path = raw_queue_path(map)

        # 5. Save
        os.makedirs(os.path.dirname(queue_path), exist_ok=True)
        with open(queue_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        return JSONResponse(content={
            "success": True,
            "message": "Queue file uploaded successfully",
            "map": map,
            "modes": list(payload.keys())
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))