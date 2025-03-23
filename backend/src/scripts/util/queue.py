import os
import json

# === Paths ===
BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..")

INPUT_DIR = os.path.join(BASE_DIR, "input")
DEFINES_DIR = os.path.join(BASE_DIR, "defines")

RAW_QUEUE_PATH = os.path.join(INPUT_DIR, "queue.json")
COMPILED_QUEUE_PATH = os.path.join(DEFINES_DIR, "queue.json")

# === Compiler ===
def compile_queue():
    if not os.path.exists(RAW_QUEUE_PATH):
        print("No raw queue.json found in input/")
        return

    with open(RAW_QUEUE_PATH, "r", encoding="utf-8") as f:
        raw_queue = json.load(f)

    compiled_queue = {}

    for mode in list(raw_queue.keys()):
        data_path = os.path.join(DEFINES_DIR, f"{mode}.json")

        if not os.path.exists(data_path):
            print(f"❌ Skipping {mode}: no defines/{mode}.json")
            continue

        with open(data_path, "r", encoding="utf-8") as f:
            region_data = json.load(f)

        # Build rgb -> region_id mapping
        rgb_to_id = {}
        for region_id, info in region_data.items():
            rgb = info.get("rgb")
            if rgb:
                rgb_to_id[rgb] = region_id

        expanded_ids = set()

        def expand(region_id):
            if region_id not in region_data:
                return
            if region_id in expanded_ids:
                return
            expanded_ids.add(region_id)

            for subject in region_data[region_id].get("subjects", []):
                expand(subject)

            overlord = region_data[region_id].get("overlord")
            if overlord:
                expand(overlord)

        # Expand from RGBs in the raw queue
        initial_rgb_list = raw_queue[mode]

        for rgb in initial_rgb_list:
            region_id = rgb_to_id.get(rgb)
            if region_id:
                expand(region_id)
            else:
                print(f"⚠️ No region found with RGB: {rgb}")

        # Convert back to RGBs for the compiled queue
        from ..mapgen.regiongen import sanitize_filename  # Adjust the import path as needed

        compiled_queue[mode] = [
            sanitize_filename(tuple(map(int, region_data[rid]["rgb"].split(","))))
            for rid in expanded_ids
            if "rgb" in region_data[rid]
        ]

    os.makedirs(DEFINES_DIR, exist_ok=True)
    with open(COMPILED_QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(compiled_queue, f, indent=2)

    print("✅ Compiled queue written to defines/queue.json")

# === Load compiled queue for generation ===
def load_queue(mode: str) -> list:
    """
    Loads the compiled queue and returns the list of regions (RGB strings) for the given mode.
    """
    if os.path.exists(COMPILED_QUEUE_PATH):
        with open(COMPILED_QUEUE_PATH, "r", encoding="utf-8") as f:
            queue = json.load(f)
            return queue.get(mode.lower(), [])
    return []

# === Save to raw input queue ===
def _save_queue(queue):
    os.makedirs(INPUT_DIR, exist_ok=True)
    with open(RAW_QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)

# === Add region to raw queue ===
def enqueue(mode: str, path: str):
    mode = mode.lower()
    queue = {}

    if os.path.exists(RAW_QUEUE_PATH):
        with open(RAW_QUEUE_PATH, "r", encoding="utf-8") as f:
            queue = json.load(f)

    if mode not in queue:
        queue[mode] = []

    if path not in queue[mode]:
        queue[mode].append(path)

    _save_queue(queue)

# === Clear raw queue by mode ===
def clear_mode(mode: str):
    mode = mode.lower()
    queue = {}

    if os.path.exists(RAW_QUEUE_PATH):
        with open(RAW_QUEUE_PATH, "r", encoding="utf-8") as f:
            queue = json.load(f)

    if mode in queue:
        del queue[mode]
        _save_queue(queue)
        print(f"Cleared all entries under mode '{mode}'.")
    else:
        print(f"No entries to clear for mode '{mode}'.")
