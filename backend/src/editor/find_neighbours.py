# Prefer: python -m scripts.map_tools.build_province_geometry <map> (from backend/src)
from PIL import Image
import numpy as np
from collections import defaultdict
import json

# -----------------------------
# Load province color mapping
# -----------------------------
def load_provinces_txt(path):
    color_to_id = {}
    with open(path, "r") as f:
        for line in f:
            if "=" not in line:
                continue
            pid, rest = line.split("=")
            pid = int(pid.strip())

            rgb_part = rest.split(";")[0]
            r, g, b = map(int, rgb_part.split(","))

            color_to_id[(r, g, b)] = pid

    return color_to_id


# -----------------------------
# Neighbor detection
# -----------------------------
def find_neighbors(image_path, color_to_id):
    img = Image.open(image_path).convert("RGB")
    data = np.array(img)

    height, width, _ = data.shape
    total_pixels = height * width
    processed = 0

    neighbors = defaultdict(set)
    BLACK = (0, 0, 0)

    # 4-directional adjacency
    directions = [
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1),
    ]

    for y in range(height):
        for x in range(width):
            processed += 1

            # Progress update (single-line)
            if processed % 100_000 == 0 or processed == total_pixels:
                percent = (processed / total_pixels) * 100
                print(
                    f"\rProcessing pixels: {processed} / {total_pixels} ({percent:.1f}%)",
                    end="",
                    flush=True,
                )

            color = tuple(data[y, x])
            if color == BLACK or color not in color_to_id:
                continue

            pid = color_to_id[color]

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    ncolor = tuple(data[ny, nx])
                    if ncolor != color and ncolor != BLACK and ncolor in color_to_id:
                        neighbors[pid].add(color_to_id[ncolor])

    print()  # newline after progress completes
    return neighbors


# -----------------------------
# Save neighbors to JSON
# -----------------------------
def save_neighbors_json(neighbors, path):
    serializable = {
        str(pid): sorted(list(nlist))
        for pid, nlist in neighbors.items()
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2)

    print(f"Saved neighbors to {path}")


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    provinces_txt = "provinces.txt"
    provinces_png = "provinces.png"
    output_json = "province_neighbors.json"

    color_to_id = load_provinces_txt(provinces_txt)
    neighbors = find_neighbors(provinces_png, color_to_id)

    save_neighbors_json(neighbors, output_json)
