from PIL import Image
import os

from ..loader.provinces import load_provinces
from ..loader.province_metadata import load_province_metadata
from ..util.dirs import input_file, validate_map


# -----------------------------
# Terrain color mapping
# -----------------------------
TERRAIN_COLORS: dict[str, tuple[int, int, int]] = {
    "plains": (80, 180, 90),
    "forest": (40, 120, 50),
    "jungle": (30, 160, 70),
    "hills": (120, 110, 90),
    "mountain": (190, 190, 190),
    "drylands": (170, 90, 40),
    "bog": (40, 109, 86),
    "farmland": (189, 41, 41),
}


# -----------------------------
# Main generator
# -----------------------------
def create_terrain_map(map_name: str, filename: str = "terrain"):
    validate_map(map_name)

    province_rgb_to_id = load_provinces(map_name)          # RGB -> province_id
    province_meta = load_province_metadata(map_name)       # province_id -> metadata

    image_path = input_file(map_name, "provinces.png")
    base_img = Image.open(image_path).convert("RGBA")
    img_data = base_img.load()

    width, height = base_img.size

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    overlay_data = overlay.load()

    # Debug counters
    total = 0
    matched = 0
    skipped_water = 0
    skipped_unknown = 0
    painted = 0

    for y in range(height):
        for x in range(width):
            total += 1

            rgb = img_data[x, y][:3]
            if rgb not in province_rgb_to_id:
                continue

            matched += 1

            pid = province_rgb_to_id[rgb]
            meta = province_meta.get(pid, {})

            terrain = meta.get("terrain")
            if terrain in ("water", "sea"):
                skipped_water += 1
                continue

            color = TERRAIN_COLORS.get(terrain)
            if not color:
                skipped_unknown += 1
                continue

            overlay_data[x, y] = (*color, 255)  # slightly stronger than fertility
            painted += 1

            # Inline progress every ~1M pixels
            if total % 1_000_000 == 0:
                print(
                    f"\rPixels: {total:,} | matched: {matched:,} | "
                    f"water: {skipped_water:,} | "
                    f"unknown: {skipped_unknown:,} | "
                    f"painted: {painted:,}",
                    end="",
                    flush=True
                )

    print(
        f"\nDONE → total: {total:,}, matched: {matched:,}, "
        f"water: {skipped_water:,}, "
        f"unknown terrain: {skipped_unknown:,}, "
        f"painted: {painted:,}"
    )

    output_path = os.path.join(
        os.path.dirname(input_file(map_name, "dummy")),
        "..", "..", "output", map_name, "maps", f"{filename}.png"
    )
    output_path = os.path.abspath(output_path)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    overlay.save(output_path, "PNG")

    print(f"🗺️ Terrain map generated → {output_path}")
