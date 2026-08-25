import os

from ..loader.provinces import load_provinces
from ..loader.province_metadata import load_province_metadata
from ..util.dirs import input_file, validate_map
from .map_paint_numpy import (
    load_provinces_array,
    paint_from_rgb_lut,
    rgba_array_to_image,
)


TERRAIN_COLORS = {
    "plains": (80, 180, 90),
    "forest": (40, 120, 50),
    "jungle": (30, 160, 70),
    "hills": (120, 110, 90),
    "mountain": (190, 190, 190),
    "drylands": (170, 90, 40),
    "bog": (40, 109, 86),
    "farmland": (189, 41, 41),
    "highlands": (73, 113, 73),
}

SKIP_TERRAINS = {"water", "sea"}


def create_terrain_map(map_name: str, filename: str = "terrain"):
    validate_map(map_name)

    # -------------------------------------------------
    # Load data
    # -------------------------------------------------
    province_rgb_to_id = load_provinces(map_name)
    province_meta = load_province_metadata(map_name)

    # -------------------------------------------------
    # Precompute province_rgb -> terrain_color
    # -------------------------------------------------
    rgb_to_color = {}

    for rgb, pid in province_rgb_to_id.items():
        meta = province_meta.get(pid)
        if not meta:
            continue

        terrain = meta.get("terrain")
        if not terrain or terrain in SKIP_TERRAINS:
            continue

        color = TERRAIN_COLORS.get(terrain)
        if color:
            rgb_to_color[rgb] = color

    # -------------------------------------------------
    # Paint
    # -------------------------------------------------
    provinces = load_provinces_array(input_file(map_name, "provinces.png"))
    painted = paint_from_rgb_lut(provinces, rgb_to_color, skip_black=False)

    # -------------------------------------------------
    # Save (fast PNG)
    # -------------------------------------------------
    output_path = os.path.abspath(
        os.path.join(
            os.path.dirname(input_file(map_name, "dummy")),
            "..", "..", "output", map_name, "maps", f"{filename}.png"
        )
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    rgba_array_to_image(painted).save(output_path, "PNG")

    print(f"🗺️ Terrain map generated → {output_path}")
