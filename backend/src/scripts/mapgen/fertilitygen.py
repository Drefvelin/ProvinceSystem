import os

from ..loader.provinces import load_provinces
from ..loader.province_metadata import load_province_metadata
from ..util.dirs import input_file, validate_map
from .map_paint_numpy import (
    load_provinces_array,
    paint_from_rgb_lut,
    rgba_array_to_image,
)


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


def fertility_to_color(fertility: int):
    fertility = max(0, min(100, fertility))

    if fertility <= 10:
        return lerp_color((120, 0, 0), (200, 0, 0), fertility / 10)
    if fertility <= 20:
        return lerp_color((200, 0, 0), (230, 180, 0), (fertility - 10) / 10)
    if fertility <= 50:
        return lerp_color((230, 180, 0), (90, 120, 40), (fertility - 20) / 30)
    return lerp_color((90, 120, 40), (80, 255, 80), (fertility - 50) / 50)


SKIP_TERRAINS = {"water", "sea"}


# -----------------------------
# FAST generator
# -----------------------------
def create_fertility_map(map_name: str, filename: str = "fertility"):
    validate_map(map_name)

    province_rgb_to_id = load_provinces(map_name)
    province_meta = load_province_metadata(map_name)

    # -------------------------------------------------
    # Precompute province_rgb -> RGBA
    # -------------------------------------------------
    rgb_to_rgba = {}

    for rgb, pid in province_rgb_to_id.items():
        meta = province_meta.get(pid)
        if not meta:
            continue

        terrain = meta.get("terrain")
        if not terrain or terrain in SKIP_TERRAINS:
            continue

        fertility = meta.get("fertility")
        if fertility is None:
            continue

        color = fertility_to_color(int(fertility))
        rgb_to_rgba[rgb] = (*color, 255)

    # -------------------------------------------------
    # Paint
    # -------------------------------------------------
    provinces = load_provinces_array(input_file(map_name, "provinces.png"))
    painted = paint_from_rgb_lut(provinces, rgb_to_rgba, skip_black=False)
    painted_pixels = int((painted[:, :, 3] > 0).sum())

    # -------------------------------------------------
    # Save output (PNG compression kept)
    # -------------------------------------------------
    output_path = os.path.abspath(
        os.path.join(
            os.path.dirname(input_file(map_name, "dummy")),
            "..", "..", "output", map_name, "maps", f"{filename}.png"
        )
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    rgba_array_to_image(painted).save(output_path, "PNG")

    print(
        f"🌱 Fertility map generated → {output_path} | "
        f"painted: {painted_pixels:,}"
    )
