from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
import os
import json

from src.scripts.util.auth import HASHED_KEY
from src.scripts.util.queue import RAW_QUEUE_PATH

router = APIRouter()

@router.post("/{hashed_key}/api/queue/upload")
async def upload_queue(hashed_key: str, request: Request):
    # 1. Validate Hash
    if hashed_key != HASHED_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        # 2. Parse full JSON queue from the request
        payload = await request.json()

        if not isinstance(payload, dict):
            raise HTTPException(status_code=400, detail="Payload must be a JSON object.")

        # 3. Save it to input/queue.json
        os.makedirs(os.path.dirname(RAW_QUEUE_PATH), exist_ok=True)
        with open(RAW_QUEUE_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        return JSONResponse(content={
            "success": True,
            "message": "Queue file uploaded successfully.",
            "modes": list(payload.keys())
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
