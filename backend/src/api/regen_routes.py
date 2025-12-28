from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from ..scripts.util.auth import HASHED_KEY
from ..scripts.util.regeneration import run_regeneration
from ..scripts.util.task_lock import regen_lock
from ..scripts.util.dirs import validate_map

import secrets

regen_router = APIRouter()

@regen_router.get("/{map}/{hashed_key}/api/regenerate/{regen_type}")
async def regenerate_map(
    map: str,
    hashed_key: str,
    regen_type: str,
    background_tasks: BackgroundTasks
):
    if not secrets.compare_digest(hashed_key, HASHED_KEY):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    # 2. Validate map
    try:
        validate_map(map)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 3. Global regen lock (safe default)
    if regen_lock.locked():
        raise HTTPException(
            status_code=429,
            detail="Regeneration already in progress."
        )

    # 4. Run regeneration in background
    background_tasks.add_task(run_regeneration, map, regen_type)

    return JSONResponse(content={
        "success": True,
        "map": map,
        "regen_type": regen_type,
        "message": (
            "Full regeneration started."
            if regen_type == "fullregen"
            else "Regeneration queued."
        )
    })