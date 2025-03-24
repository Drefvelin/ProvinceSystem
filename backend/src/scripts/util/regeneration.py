import asyncio
from concurrent.futures import ThreadPoolExecutor
from src.scripts.compile.nation_compiler import process_nations
from src.scripts.mapgen.mapgen import create_map
from src.scripts.mapgen.regiongen import generate_regions
from src.scripts.util.queue import load_queue, compile_queue

executor = ThreadPoolExecutor()
regen_lock = asyncio.Lock()

async def run_regeneration(regen_type: str):
    """
    Triggers regeneration for all modes.
    If regen_type is "queued", only regenerate modes with entries in the queue.
    """
    async with regen_lock:
        def sync_task():
            modes = ["nation", "duchy", "kingdom", "county"]

            # Compile queue before starting
            compile_queue()
            queue = load_queue()  # Loads full compiled queue

            for mode in modes:
                if regen_type.lower() != "fullregen":
                    if mode not in queue or not queue[mode]:
                        print(f"🔁 Skipping {mode} — empty queue")
                        continue

                if mode == "nation":
                    process_nations()

                create_map(mode, f"{mode}_map", True)
                generate_regions(mode, borders=True, frontend_save=True, queued_regen=(regen_type.lower() != "fullregen"))

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, sync_task)