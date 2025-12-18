import os

# === Base ===
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
# BASE_DIR -> backend/src

# === High-level dirs ===
INPUT_DIR = os.path.join(BASE_DIR, "input")
DEFINES_DIR = os.path.join(BASE_DIR, "defines")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# === Input ===
def input_file(map_name: str, filename: str) -> str:
    return os.path.join(INPUT_DIR, map_name, filename)

# === Defines ===
def defines_file(map_name: str, filename: str) -> str:
    return os.path.join(DEFINES_DIR, map_name, filename)

# === Output ===
def map_image(map_name: str, map_type: str) -> str:
    return os.path.join(OUTPUT_DIR, map_name, "maps", f"{map_type}_map.png")

def region_image(map_name: str, type: str, filename: str) -> str:
    return os.path.join(OUTPUT_DIR, map_name, "regions", type, filename)

def banner_image(map_name: str, filename: str) -> str:
    return os.path.join(OUTPUT_DIR, map_name, "banners", filename)

def validate_map(map_name: str):
    if not map_name.isalnum():
        raise ValueError("Invalid map name")