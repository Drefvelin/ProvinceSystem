from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from src.scripts.util.auth import HASHED_KEY
from src.scripts.util.regeneration import run_regeneration
from src.scripts.util.task_lock import regen_lock

import concurrent.futures

router = APIRouter()
executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)  # Optional: tune this if needed

@router.get("/{hashed_key}/api/regenerate/{regen_type}")
async def regenerate_map(
    hashed_key: str,
    regen_type: str,
    background_tasks: BackgroundTasks
):
    if hashed_key != HASHED_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if regen_lock.locked():
        raise HTTPException(status_code=429, detail="Regeneration already in progress.")

    background_tasks.add_task(run_regeneration, regen_type)

    return JSONResponse(content={
        "success": True,
        "regen_type": regen_type,
        "message": f"{'Queued' if regen_type != 'fullregen' else 'Full'} regeneration started."
    })



