from PIL import Image
import os

from ..util.colour_mapping import build_color_mapping, get_color_overrides
from ..util.border_paint import paint_borders
from ..util.dirs import input_file, validate_map


def create_map(map_name: str, mode: str, filename: str):
    validate_map(map_name)

    province_to_color = build_color_mapping(map_name, mode)
    overrides = get_color_overrides(map_name, mode)

    base_img = Image.open(input_file(map_name, "provinces.png")).convert("RGBA")
    src = base_img.load()
    width, height = base_img.size

    out = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    dst = out.load()

    if overrides:
        for y in range(height):
            for x in range(width):
                rgb = src[x, y][:3]
                color = province_to_color.get(rgb)
                if not color:
                    continue
                color = overrides.get(color, color)
                dst[x, y] = (*color, 255)
    else:
        for y in range(height):
            for x in range(width):
                color = province_to_color.get(src[x, y][:3])
                if color:
                    dst[x, y] = (*color, 255)

    paint_borders(True, True, dst, width, height)

    output_path = os.path.abspath(
        os.path.join(
            os.path.dirname(input_file(map_name, "dummy")),
            "..", "..", "output", map_name, "maps", f"{filename}.png"
        )
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    out.save(output_path, "PNG")

    print(f"🗺️ Map generated for '{map_name}' → {output_path}")