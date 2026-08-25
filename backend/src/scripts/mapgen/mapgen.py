import os
import time

from ..util.colour_mapping import build_color_mapping, get_color_overrides
from ..util.border_paint import paint_borders
from ..util.dirs import input_file, validate_map
from .geometry_cache import MapGeometryCache
from .map_paint_numpy import (
    load_provinces_array,
    paint_from_province_id_lut,
    paint_from_rgb_lut,
    rgba_array_to_image,
)


def create_map(
    map_name: str,
    mode: str,
    filename: str,
    borders: bool = True,
    # IMPORTANT:
    # For frontend picking/canvas reference this MUST stay False,
    # otherwise vassals get overwritten by overlord colours and become un-pickable.
    # Pick maps must also keep raw nation rgb — never call display_colour.display_rgb here.
    apply_overrides: bool = False,
    cache: MapGeometryCache | None = None,
):
    """
    Creates a single full map image from provinces.png using the mapping for `mode`.

    - When apply_overrides=False (default): produces a *pick-safe* map where each region’s own RGB exists.
    - When apply_overrides=True: vassal pixels are replaced by their overlord colour.
    - Display muting for hover/drill overlays lives in regiongen.py only.
    """
    start_time = time.perf_counter()
    validate_map(map_name)

    province_to_color = build_color_mapping(map_name, mode)

    if cache is not None:
        provinces = cache.provinces_rgba
        height, width = cache.height, cache.width
    else:
        provinces = load_provinces_array(input_file(map_name, "provinces.png"))
        height, width = provinces.shape[:2]

    # --------------------------------------------------------------
    # Output path
    # --------------------------------------------------------------
    output_path = os.path.abspath(
        os.path.join(
            os.path.dirname(input_file(map_name, "dummy")),
            "..", "..", "output", map_name, "maps", f"{filename}.png"
        )
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # --------------------------------------------------------------
    # Empty mapping → transparent output
    # --------------------------------------------------------------
    if not province_to_color:
        if cache is not None:
            painted = paint_from_province_id_lut(
                cache.province_id_map,
                cache.rgb_to_id,
                {},
            )
        else:
            painted = paint_from_rgb_lut(provinces, {})
        rgba_array_to_image(painted).save(output_path, "PNG")
        print(f"🗺️ Empty map generated → {output_path}")
        return

    overrides = get_color_overrides(map_name, mode) if apply_overrides else None

    if cache is not None:
        painted = paint_from_province_id_lut(
            cache.province_id_map,
            cache.rgb_to_id,
            province_to_color,
            skip_black=True,
            color_overrides=overrides,
        )
    else:
        painted = paint_from_rgb_lut(
            provinces,
            province_to_color,
            skip_black=True,
            color_overrides=overrides,
        )
    out = rgba_array_to_image(painted)

    # --------------------------------------------------------------
    # Borders
    # --------------------------------------------------------------
    if borders:
        paint_borders(True, True, out.load(), width, height)

    # --------------------------------------------------------------
    # Save output
    # --------------------------------------------------------------
    out.save(output_path, "PNG")

    elapsed = time.perf_counter() - start_time
    print(
        f"🗺️ Map generated for '{map_name}' "
        f"(mode={mode}, borders={borders}, apply_overrides={apply_overrides}) "
        f"in {elapsed:.2f}s → {output_path}"
    )
