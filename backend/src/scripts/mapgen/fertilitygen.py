from PIL import Image
import os

from ..loader.provinces import load_provinces
from ..loader.province_metadata import load_province_metadata
from ..util.dirs import input_file, validate_map


# -----------------------------
# Color interpolation helpers
# -----------------------------
def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float):
    return (
        lerp(c1[0], c2[0], t),
        lerp(c1[1], c2[1], t),
        lerp(c1[2], c2[2], t),
    )


def fertility_to_color(fertility: int) -> tuple[int, int, int]:
    fertility = max(0, min(100, fertility))

    if fertility <= 10:
        return lerp_color((120, 0, 0), (200, 0, 0), fertility / 10)

    if fertility <= 20:
        return lerp_color((200, 0, 0), (230, 180, 0), (fertility - 10) / 10)

    if fertility <= 50:
        return lerp_color((230, 180, 0), (90, 120, 40), (fertility - 20) / 30)

    return lerp_color((90, 120, 40), (80, 255, 80), (fertility - 50) / 50)


# -----------------------------
# Main generator
# -----------------------------
def create_fertility_map(map_name: str, filename: str = "fertility"):
    validate_map(map_name)

    # Load mappings
    province_rgb_to_id = load_provinces(map_name)          # RGB -> province_id
    province_meta = load_province_metadata(map_name)       # province_id -> metadata

    # Load province map image
    image_path = input_file(map_name, "provinces.png")
    base_img = Image.open(image_path).convert("RGBA")
    img_data = base_img.load()

    width, height = base_img.size

    # Transparent overlay
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    overlay_data = overlay.load()

    # -----------------------------
    # Debug counters
    # -----------------------------
    total = 0
    matched = 0
    skipped_water = 0
    skipped_no_fertility = 0
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

            # ✅ ONLY skip water / sea
            terrain = meta.get("terrain")
            if terrain in ("water", "sea"):
                skipped_water += 1
                continue

            fertility = meta.get("fertility")
            if fertility is None:
                skipped_no_fertility += 1
                continue

            color = fertility_to_color(int(fertility))
            overlay_data[x, y] = (*color, 160)  # alpha controls overlay strength
            painted += 1

            # Inline progress update (every ~1M pixels)
            if total % 1_000_000 == 0:
                print(
                    f"\rPixels: {total:,} | matched: {matched:,} | "
                    f"water: {skipped_water:,} | "
                    f"no fertility: {skipped_no_fertility:,} | "
                    f"painted: {painted:,}",
                    end="",
                    flush=True
                )

    # Final debug summary
    print(
        f"\nDONE → total: {total:,}, matched: {matched:,}, "
        f"water: {skipped_water:,}, "
        f"no fertility: {skipped_no_fertility:,}, "
        f"painted: {painted:,}"
    )

    # Save output
    output_path = os.path.join(
        os.path.dirname(input_file(map_name, "dummy")),
        "..", "..", "output", map_name, "maps", f"{filename}.png"
    )
    output_path = os.path.abspath(output_path)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    overlay.save(output_path, "PNG")

    print(f"🌱 Fertility map generated → {output_path}")
