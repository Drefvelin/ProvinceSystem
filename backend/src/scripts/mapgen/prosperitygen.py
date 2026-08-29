import os
import json
import math

from ..loader.provinces import load_provinces
from ..loader.province_metadata import load_province_metadata
from ..util.dirs import input_file, validate_map
from .geometry_cache import MapGeometryCache
from .map_paint_numpy import (
    load_provinces_array,
    paint_from_rgb_lut,
    rgba_array_to_image,
)


SKIP_TERRAINS = {"water", "sea"}


# -----------------------------
# Color interpolation helpers
# -----------------------------
def lerp(a: int, b: int, t: float) -> int:
    return min(255, max(0, int(a + (b - a) * t)))


def lerp_color(c1, c2, t: float):
    return (
        lerp(c1[0], c2[0], t),
        lerp(c1[1], c2[1], t),
        lerp(c1[2], c2[2], t),
    )


def prosperity_to_color(norm: float):
    """
    norm ∈ [0, 1]
    """
    if norm <= 0.33:
        return lerp_color((120, 0, 0), (220, 0, 0), norm / 0.33)
    if norm <= 0.66:
        return lerp_color((220, 0, 0), (230, 180, 0), (norm - 0.33) / 0.33)
    return lerp_color((230, 180, 0), (120, 220, 120), (norm - 0.66) / 0.34)


def prosperity_to_alpha(norm: float) -> int:
    """
    Lower prosperity = more transparent
    Higher prosperity = more opaque
    """
    norm = max(0.0, min(1.0, norm))

    # Soft curve so low prosperity barely shows
    alpha = 40 + int(215 * (norm ** 0.8))
    return min(255, max(0, alpha))


# -----------------------------
# FAST generator (logarithmic)
# -----------------------------
def create_prosperity_map(
    map_name: str,
    filename: str = "prosperity",
    cache: MapGeometryCache | None = None,
):
    validate_map(map_name)

    province_rgb_to_id = load_provinces(map_name)
    province_meta = load_province_metadata(map_name)

    with open(input_file(map_name, "province_data.json"), "r") as f:
        province_data = json.load(f)

    province_by_id = {p["id"]: p for p in province_data}

    # -------------------------------------------------
    # Compute min / max prosperity
    # -------------------------------------------------
    prosperities = [
        p.get("prosperity", 0)
        for p in province_data
        if p.get("prosperity", 0) > 0
    ]

    if not prosperities:
        print("⚠ No prosperity data found")
        return

    min_prosperity = min(prosperities)
    max_prosperity = max(prosperities)

    if max_prosperity <= min_prosperity:
        print("⚠ Invalid prosperity range")
        return

    # Log-space bounds
    log_min = math.log1p(min_prosperity)
    log_max = math.log1p(max_prosperity)
    inv_log_range = 1.0 / (log_max - log_min)

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

        pdata = province_by_id.get(pid)
        if not pdata:
            continue

        prosperity = pdata.get("prosperity", 0)
        if prosperity <= 0:
            continue

        # Log-scaled normalization (ordering preserved)
        log_val = math.log1p(prosperity)
        norm = (log_val - log_min) * inv_log_range
        norm = max(0.0, min(1.0, norm))

        # Light compression so greens don't dominate
        norm = norm ** 0.85

        color = prosperity_to_color(norm)
        alpha = prosperity_to_alpha(norm)

        rgb_to_rgba[rgb] = (*color, alpha)

    # -------------------------------------------------
    # Paint
    # -------------------------------------------------
    if cache is not None:
        provinces = cache.provinces_rgba
    else:
        provinces = load_provinces_array(input_file(map_name, "provinces.png"))
    painted = paint_from_rgb_lut(provinces, rgb_to_rgba, skip_black=False)
    painted_pixels = int((painted[:, :, 3] > 0).sum())

    # -------------------------------------------------
    # Save
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
        f"🔥 Prosperity map generated → {output_path} | "
        f"min={min_prosperity:.2f} | max={max_prosperity:.2f} | "
        f"painted={painted_pixels:,}"
    )
