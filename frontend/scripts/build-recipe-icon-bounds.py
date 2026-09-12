"""Measure transparent padding for recipe icons without modifying source PNGs.

Run from any directory: python frontend/scripts/build-recipe-icon-bounds.py
Requires Pillow. Re-run after extracting or replacing wiki textures.
Only off-centre images need metadata; fully transparent/centred images are omitted.
"""

import json
from pathlib import Path

from PIL import Image


def measure_bounds(texture_root: Path) -> dict[str, list[int]]:
    measured = {}
    for path in sorted(texture_root.rglob("*.png")):
        # Vehicle atlases are rendered by the model viewer, not as recipe icons.
        if path.relative_to(texture_root).parts[0] == "vehicles":
            continue
        with Image.open(path) as image:
            width, height = image.size
            bounds = image.convert("RGBA").getchannel("A").getbbox()
        if bounds is None:
            continue
        left, top, right, bottom = bounds
        if left + right == width and top + bottom == height:
            continue
        url = "/wiki/textures/" + path.relative_to(texture_root).as_posix()
        measured[url] = [width, height, left, top, right, bottom]
    return measured


if __name__ == "__main__":
    frontend = Path(__file__).resolve().parents[1]
    output = frontend / "app/wiki/data/generated/recipeIconBounds.json"
    measured = measure_bounds(frontend / "public/wiki/textures")
    output.write_text(json.dumps(measured, indent=2) + "\n", encoding="utf-8")
    print(f"Measured {len(measured)} off-centre recipe textures; source PNGs unchanged.")
