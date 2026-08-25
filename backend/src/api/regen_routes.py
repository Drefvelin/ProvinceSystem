from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from fastapi.responses import JSONResponse
import secrets

from .internal_access import require_localhost
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
    background_tasks: BackgroundTasks,
    request: Request,
):
    require_localhost(request)

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
        "message": _regen_start_message(regen_type),
    })


def _regen_start_message(regen_type: str) -> str:
    lower = regen_type.lower()
    if lower == "fullregen":
        return "Full regeneration started."
    if lower.startswith("fullregen:"):
        mode = lower.split(":", 1)[1]
        return f"Full regeneration started for mode '{mode}'."
    if lower.startswith("queued"):
        return "Queued regeneration started."
    if lower == "textonly":
        return "Text-only compile started."
    return "Regeneration started."
