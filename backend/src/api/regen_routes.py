from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from src.scripts.util.auth import HASHED_KEY
from src.scripts.mapgen.mapgen import create_map
from src.scripts.mapgen.regiongen import generate_regions
from src.scripts.compile.nation_compiler import process_nations
from src.scripts.util.task_lock import regen_lock

router = APIRouter()

@router.get("/{hashed_key}/api/regenerate/{mode}/{regen_type}")
async def regenerate_map(
    hashed_key: str,
    mode: str,
    regen_type: str,
    background_tasks: BackgroundTasks
):
    if hashed_key != HASHED_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # === Check if regen is already running ===
    if regen_lock.locked():
        raise HTTPException(status_code=429, detail="Regeneration is already in progress.")

    # === Background task logic ===
    async def background_job():
        async with regen_lock:
            try:
                if mode.lower() == "nation":
                    process_nations()

                queued = regen_type.lower() != "fullregen"
                create_map(mode, mode + "_map", True)
                generate_regions(mode, borders=True, frontend_save=True, queued_regen=queued)
            except Exception as e:
                print(f"[ERROR] Regeneration failed for {mode}: {str(e)}")

    background_tasks.add_task(background_job)

    return JSONResponse(content={
        "success": True,
        "mode": mode,
        "regen_type": regen_type,
        "message": f"{'Queued' if regen_type != 'fullregen' else 'Full'} regeneration started for {mode}."
    })

