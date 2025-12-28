from PIL import Image
import numpy as np

FOUND_COLOR = (0, 255, 0)   # green for land provinces
BLACK = (0, 0, 0)
WATER_TERRAINS = {"water", "sea"}

PROGRESS_INTERVAL = 250_000  # pixels between console updates

# -----------------------------
# Load provinces.txt
# -----------------------------
def load_provinces_txt(path):
    """
    Returns:
        id_to_data: { pid: (rgb_tuple, terrain) }
    """
    id_to_data = {}

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" not in line:
                continue

            # Expected format:
            # id = r,g,b;terrain;fertility
            left, right = line.split("=")
            pid = int(left.strip())

            parts = right.strip().split(";")
            if len(parts) < 2:
                continue

            r, g, b = map(int, parts[0].split(","))
            terrain = parts[1].strip().lower()

            id_to_data[pid] = ((r, g, b), terrain)

    return id_to_data


# -----------------------------
# Main
# -----------------------------
def main():
    provinces_txt = "provinces.txt"
    provinces_png = "provinces.png"
    output_png = "province_validation.png"

    id_to_data = load_provinces_txt(provinces_txt)

    # Build fast lookup: rgb -> terrain
    color_to_terrain = {
        rgb: terrain
        for (rgb, terrain) in id_to_data.values()
    }

    defined_colors = set(color_to_terrain.keys())

    img = Image.open(provinces_png).convert("RGB")
    img_np = np.array(img)

    height, width, _ = img_np.shape
    total_pixels = height * width
    processed = 0

    found_colors = set()

    # Scan image
    for y in range(height):
        for x in range(width):
            processed += 1

            # Progress output
            if processed % PROGRESS_INTERVAL == 0 or processed == total_pixels:
                percent = (processed / total_pixels) * 100
                print(
                    f"\rScanning PNG: {processed:,} / {total_pixels:,} pixels ({percent:.1f}%)",
                    end="",
                    flush=True
                )

            color = tuple(img_np[y, x])
            if color == BLACK:
                continue

            if color in defined_colors:
                found_colors.add(color)

                terrain = color_to_terrain[color]
                if terrain in WATER_TERRAINS:
                    img_np[y, x] = BLACK
                else:
                    img_np[y, x] = FOUND_COLOR

    print()  # newline after progress completes

    # Determine missing provinces
    missing = [
        pid for pid, (rgb, _) in id_to_data.items()
        if rgb not in found_colors
    ]

    # Save visualization
    Image.fromarray(img_np).save(output_png)

    # Console output
    print("=== Province Validation Report ===")
    print(f"Total defined provinces: {len(id_to_data)}")
    print(f"Provinces found on PNG: {len(found_colors)}")
    print(f"Missing provinces: {len(missing)}\n")

    if missing:
        print("Provinces defined in provinces.txt but NOT found on the PNG:")
        for pid in sorted(missing):
            rgb, terrain = id_to_data[pid]
            print(f"  Province {pid} (RGB {rgb}, terrain={terrain})")
    else:
        print("All provinces were found on the PNG.")

    print(f"\nValidation image written to: {output_png}")


if __name__ == "__main__":
    main()
