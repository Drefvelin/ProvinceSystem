import asyncio
from concurrent.futures import ThreadPoolExecutor
from src.scripts.compile.nation_compiler import process_nations
from src.scripts.mapgen.mapgen import create_map
from src.scripts.mapgen.regiongen import generate_regions

# Shared thread pool
executor = ThreadPoolExecutor()
regen_lock = asyncio.Lock()  # You can optionally pass this from outside if needed

async def run_regeneration(mode: str, regen_type: str):
    """
    Triggers regeneration for a given mode ('nation', 'duchy', etc.)
    and regen type ('queued' or 'fullregen').
    """

    async with regen_lock:
        def sync_task():
            if mode.lower() == "nation":
                process_nations()
            if regen_type.lower() == "textonly":
                return

            queued = regen_type.lower() != "fullregen"
            create_map(mode, mode + "_map", True)
            generate_regions(mode, borders=True, frontend_save=True, queued_regen=queued)

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, sync_task)
