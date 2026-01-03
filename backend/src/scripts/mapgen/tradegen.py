from PIL import Image
import os

from ..util.dirs import input_file, validate_map
from ..util.border_paint import paint_borders
from ..util.colour_mapping import build_color_mapping


def create_trade_map(
    map_name: str,
    filename: str = "trade",
    borders: bool = False
):
    validate_map(map_name)

    province_to_color = build_color_mapping(map_name, mode="guild")

    base_img = Image.open(input_file(map_name, "provinces.png")).convert("RGBA")
    img_data = base_img.load()
    width, height = base_img.size

    out_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    out_data = out_img.load()

    # -------------------------------------------------
    # SINGLE PASS PAINT (FAST)
    # -------------------------------------------------
    for y in range(height):
        for x in range(width):
            rgb = img_data[x, y][:3]
            color = province_to_color.get(rgb)
            if color:
                out_data[x, y] = (*color, 255)

    # -------------------------------------------------
    # Borders (optional)
    # -------------------------------------------------
    if borders:
        paint_borders(True, True, out_data, width, height)

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
    out_img.save(output_path, "PNG")
