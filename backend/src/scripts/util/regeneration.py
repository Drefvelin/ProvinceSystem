import asyncio
from concurrent.futures import ThreadPoolExecutor
from src.scripts.compile.nation_compiler import process_nations
from src.scripts.mapgen.mapgen import create_map
from src.scripts.mapgen.regiongen import generate_regions
from src.scripts.util.queue import load_queue, compile_queue
import os
import json

executor = ThreadPoolExecutor()
regen_lock = asyncio.Lock()

RAW_QUEUE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "input", "queue.json")
COMPILED_QUEUE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "defines", "queue.json")

def print_queues():
    print("📥 RAW QUEUE (input/queue.json):")
    if os.path.exists(RAW_QUEUE_PATH):
        with open(RAW_QUEUE_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
            print(json.dumps(raw, indent=2))
    else:
        print("❌ No raw queue file found.")

    print("\n📦 COMPILED QUEUE (defines/queue.json):")
    if os.path.exists(COMPILED_QUEUE_PATH):
        with open(COMPILED_QUEUE_PATH, "r", encoding="utf-8") as f:
            compiled = json.load(f)
            print(json.dumps(compiled, indent=2))
    else:
        print("❌ No compiled queue file found.")

def run_regeneration(regen_type: str):
    print("🔁 Regeneration task started")  # ✅ debug

    def sync_task():
        print("🔧 Sync task starting...")
        modes = ["nation", "duchy", "kingdom", "county", "empire"]
        process_nations()

        compile_queue()
        print("✅ Queue compiled")
        print_queues()  # 👈 Add this here

        if regen_type.lower() != "textonly":
            for mode in modes:
                queue = load_queue(mode)
                if regen_type.lower() != "fullregen":
                    if not queue:
                        print(f"⚠️ Skipping {mode}: Empty queue")
                        continue

                print(f"🛠️ Processing mode: {mode}")

                create_map(mode, f"{mode}_map", True)
                print(f"🗺️ Map generated for {mode}")

                generate_regions(mode, borders=True, frontend_save=True, queued_regen=(regen_type.lower() != "fullregen"))
                print(f"🎨 Regions generated for {mode}")

        print("✅ Regeneration complete.")
    sync_task()