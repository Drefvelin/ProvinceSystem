from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import secrets

from ..scripts.util.auth import HASHED_KEY
from ..scripts.util.regeneration import run_regeneration
from ..scripts.util.task_lock import get_map_lock
from ..scripts.util.dirs import validate_map

regen_router = APIRouter()

@regen_router.get("/{map}/{hashed_key}/api/regenerate/{regen_type}")
async def regenerate_map(
    map: str,
    hashed_key: str,
    regen_type: str,
    background_tasks: BackgroundTasks
):
    # 1. Auth
    if not secrets.compare_digest(hashed_key, HASHED_KEY):
        raise HTTPException(status_code=401, detail="Invalid API key")

    # 2. Validate map
    try:
        validate_map(map)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 3. Per-map lock check
    map_lock = get_map_lock(map)
    if map_lock.locked():
        raise HTTPException(
            status_code=429,
            detail=f"Regeneration already in progress for map '{map}'."
        )

    # 4. Start background regeneration
    background_tasks.add_task(run_regeneration, map, regen_type)

    return JSONResponse(content={
        "success": True,
        "map": map,
        "regen_type": regen_type,
        "message": (
            "Full regeneration started."
            if regen_type.lower() == "fullregen"
            else "Regeneration queued."
        )
    })
