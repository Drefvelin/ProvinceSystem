import asyncio
from concurrent.futures import ThreadPoolExecutor

from ..compile.nation_compiler import process_nations
from ..mapgen.mapgen import create_map
from ..mapgen.regiongen import generate_regions
from .queue import load_queue, compile_queue
from .dirs import (
    validate_map,
    input_file,
    defines_file
)

import os
import json

executor = ThreadPoolExecutor()
regen_lock = asyncio.Lock()


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


def run_regeneration(map_name: str, regen_type: str):
    validate_map(map_name)

    print(f"🔁 Regeneration started for map '{map_name}'")

    def sync_task():
        print("🔧 Sync task starting...")

        modes = ["nation", "duchy", "kingdom", "county", "empire"]

        # 1. Compile nation data
        process_nations(map_name)

        # 2. Compile queue
        compile_queue(map_name)
        print("✅ Queue compiled")
        print_queues(map_name)

        # 3. Generate maps + regions
        if regen_type.lower() != "textonly":
            for mode in modes:
                queue = load_queue(map_name, mode)

                if regen_type.lower() != "fullregen" and not queue:
                    print(f"⚠️ Skipping {mode}: Empty queue")
                    continue

                print(f"🛠️ [{map_name}] Processing mode: {mode}")

                create_map(map_name, mode, f"{mode}_map")
                print(f"🗺️ [{map_name}] Map generated for {mode}")

                generate_regions(
                    map_name,
                    mode,
                    borders=True,
                    queued_regen=(regen_type.lower() != "fullregen")
                )
                print(f"🎨 [{map_name}] Regions generated for {mode}")

        print(f"✅ Regeneration complete for map '{map_name}'")

    sync_task()