import json
import os

from ..loader.provinces import load_provinces
from ..loader.province_metadata import load_province_metadata
from ..util.dirs import input_file, validate_map
from .map_paint_numpy import (
    load_provinces_array,
    paint_from_rgb_lut,
    rgba_array_to_image,
)

SKIP_TERRAINS = {"water", "sea"}

# Yellow (mild) -> orange -> red -> dark red (extreme). No green.
SEVERITY_RGBA = {
    "mild": (230, 200, 40, 220),
    "worrying": (220, 120, 20, 230),
    "severe": (180, 20, 20, 240),
    "extreme": (90, 0, 0, 255),
}


def infestation_to_rgba(severity: str) -> tuple[int, int, int, int] | None:
    if not severity:
        return None
    return SEVERITY_RGBA.get(str(severity).strip().lower())


def load_infestation_by_id(map_name: str) -> dict[int, dict]:
    path = input_file(map_name, "infestation_data.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict):
        rows = data.get("provinces") or []
    else:
        return {}
    out: dict[int, dict] = {}
    for row in rows:
        if not isinstance(row, dict) or "id" not in row:
            continue
        try:
            pid = int(row["id"])
        except (TypeError, ValueError):
            continue
        out[pid] = row
    return out


def create_infestation_map(
    map_name: str,
    filename: str = "infestation_map",
    cache=None,
):
    validate_map(map_name)

    province_rgb_to_id = load_provinces(map_name)
    province_meta = load_province_metadata(map_name)
    by_id = load_infestation_by_id(map_name)

    rgb_to_rgba = {}
    for rgb, pid in province_rgb_to_id.items():
        meta = province_meta.get(pid)
        if not meta:
            continue
        terrain = meta.get("terrain")
        if not terrain or terrain in SKIP_TERRAINS:
            continue
        row = by_id.get(pid)
        if row is None:
            try:
                row = by_id.get(int(pid))
            except (TypeError, ValueError):
                row = None
        if not row:
            continue
        color = infestation_to_rgba(row.get("severity"))
        if color is None:
            continue
        rgb_to_rgba[rgb] = color

    provinces = load_provinces_array(input_file(map_name, "provinces.png"))
    painted = paint_from_rgb_lut(provinces, rgb_to_rgba, skip_black=False)
    painted_pixels = int((painted[:, :, 3] > 0).sum())

    output_path = os.path.abspath(
        os.path.join(
            os.path.dirname(input_file(map_name, "dummy")),
            "..",
            "..",
            "output",
            map_name,
            "maps",
            f"{filename}.png",
        )
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    rgba_array_to_image(painted).save(output_path, "PNG")

    print(
        f"Infestation map generated -> {output_path} | "
        f"painted: {painted_pixels:,} | infestations: {len(by_id)}"
    )
