from PIL import Image
import os
import json

from ..loader.provinces import load_provinces
from ..loader.province_metadata import load_province_metadata
from ..util.dirs import input_file, validate_map


SKIP_TERRAINS = {"water", "sea"}


# -----------------------------
# Color interpolation helpers
# -----------------------------
def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def lerp_color(c1, c2, t: float):
    return (
        lerp(c1[0], c2[0], t),
        lerp(c1[1], c2[1], t),
        lerp(c1[2], c2[2], t),
    )


def prosperity_to_color(norm: float):
    if norm <= 0.33:
        return lerp_color((120, 0, 0), (220, 0, 0), norm / 0.33)
    if norm <= 0.66:
        return lerp_color((220, 0, 0), (230, 180, 0), (norm - 0.33) / 0.33)
    return lerp_color((230, 180, 0), (80, 255, 80), (norm - 0.66) / 0.34)


# -----------------------------
# FAST generator
# -----------------------------
def create_prosperity_map(map_name: str, filename: str = "prosperity"):
    validate_map(map_name)

    province_rgb_to_id = load_provinces(map_name)
    province_meta = load_province_metadata(map_name)

    with open(input_file(map_name, "province_data.json"), "r") as f:
        province_data = json.load(f)

    province_by_id = {p["id"]: p for p in province_data}

    # -------------------------------------------------
    # Compute max prosperity
    # -------------------------------------------------
    max_prosperity = max(
        (p.get("prosperity", 0) for p in province_data),
        default=1.0
    )

    if max_prosperity <= 0:
        print("⚠ No prosperity data found")
        return

    inv_max = 1.0 / max_prosperity

    # -------------------------------------------------
    # Precompute province_rgb -> RGBA color
    # -------------------------------------------------
    rgb_to_rgba = {}

    for rgb, pid in province_rgb_to_id.items():
        meta = province_meta.get(pid)
        if not meta:
            continue

        terrain = meta.get("terrain")
        if not terrain or terrain in SKIP_TERRAINS:
            continue

        pdata = province_by_id.get(pid)
        if not pdata:
            continue

        prosperity = pdata.get("prosperity", 0)
        if prosperity <= 0:
            continue

        norm = prosperity * inv_max
        color = prosperity_to_color(norm)
        rgb_to_rgba[rgb] = (*color, 255)

    # -------------------------------------------------
    # Load base image
    # -------------------------------------------------
    base_img = Image.open(input_file(map_name, "provinces.png")).convert("RGBA")
    src = base_img.load()
    width, height = base_img.size

    out = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    dst = out.load()

    # -------------------------------------------------
    # FAST SINGLE-PASS PAINT
    # -------------------------------------------------
    painted = 0
    for y in range(height):
        for x in range(width):
            rgba = rgb_to_rgba.get(src[x, y][:3])
            if rgba:
                dst[x, y] = rgba
                painted += 1

    # -------------------------------------------------
    # Save (keep PNG compression)
    # -------------------------------------------------
    output_path = os.path.abspath(
        os.path.join(
            os.path.dirname(input_file(map_name, "dummy")),
            "..", "..", "output", map_name, "maps", f"{filename}.png"
        )
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    out.save(output_path, "PNG")

    print(
        f"🔥 Prosperity map generated → {output_path} | "
        f"max={max_prosperity:.2f} | painted={painted:,}"
    )
