import asyncio
import os
import json
import sys
import time

from ..compile.nation_compiler import process_nations
from ..compile.trade_compiler import process_trade
from ..mapgen.mapgen import create_map
from ..mapgen.prosperitygen import create_prosperity_map
from ..mapgen.regiongen import generate_regions
from .queue import load_queue, compile_queue
from .dirs import (
    validate_map,
    input_file,
    defines_file
)
from .task_lock import get_map_lock


def print_queues(map_name: str):
    raw_path = input_file(map_name, "queue.json")
    compiled_path = defines_file(map_name, "queue.json")

    print(f"📥 RAW QUEUE ({raw_path}):")
    if os.path.exists(raw_path):
        with open(raw_path, "r", encoding="utf-8") as f:
            print(json.dumps(json.load(f), indent=2))
    else:
        print("❌ No raw queue file found.")

    print(f"\n📦 COMPILED QUEUE ({compiled_path}):")
    if os.path.exists(compiled_path):
        with open(compiled_path, "r", encoding="utf-8") as f:
            print(json.dumps(json.load(f), indent=2))
    else:
        print("❌ No compiled queue file found.")


# -------------------------
# Sync regeneration logic
# -------------------------
def _sync_regeneration(map_name: str, regen_type: str):
    # Windows consoles often default to cp1252; regen logs use UTF-8 symbols.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    start_time = time.perf_counter()

    validate_map(map_name)
    print(f"🔁 Regeneration started for map '{map_name}'")

    modes = ["nation", "duchy", "kingdom", "county", "empire", "trade"]

    # 1. Compile nation data
    process_nations(map_name)
    if map_name == "dev":
       process_trade(map_name)

    # 2. Compile queue
    compile_queue(map_name)
    print("✅ Queue compiled")
    print_queues(map_name)

    # 3. Generate maps + regions
    if regen_type.lower() != "textonly":
        for mode in modes:
            if map_name != "dev" and mode == "trade":
                print(f"⚠️ Skipping {mode}: Incompatible Map")
                continue
            queue = load_queue(map_name, mode)

            if regen_type.lower() != "fullregen" and not mode == "trade" and not queue:
                print(f"⚠️ Skipping {mode}: Empty queue")
                continue

            print(f"🛠️ [{map_name}] Processing mode: {mode}")

            if mode == "trade":
                create_prosperity_map(map_name, "prosperity_map")

            create_map(map_name, mode, f"{mode}_map", False)
            print(f"🗺️ [{map_name}] Map generated for {mode}")

            generate_regions(
                map_name,
                mode,
                borders=mode != "trade",
                queued_regen=(regen_type.lower() != "fullregen" and not mode == "trade")
            )
            print(f"🎨 [{map_name}] Regions generated for {mode}")

    elapsed = time.perf_counter() - start_time

    print(
        f"⏱️ Regeneration for map '{map_name}' "
        f"(type: {regen_type}) took {elapsed:.2f} seconds"
    )
    print(f"✅ Regeneration complete for map '{map_name}'")


# -------------------------
# Async entry point
# -------------------------
async def run_regeneration(map_name: str, regen_type: str):
    lock = get_map_lock(map_name)

    async with lock:
        # Run blocking work off the event loop
        await asyncio.to_thread(_sync_regeneration, map_name, regen_type)