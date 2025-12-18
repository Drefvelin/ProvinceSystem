from PIL import Image
import os

from ..util.colour_mapping import build_color_mapping, get_color_overrides
from ..util.border_paint import paint_borders
from ..util.flood_fill import flood_fill
from ..util.dirs import (
    input_file,
    validate_map
)


def create_map(map_name: str, mode: str, filename: str):
    validate_map(map_name)

    # Create lookup dictionaries
    province_to_color = build_color_mapping(map_name, mode)
    overrides = get_color_overrides(map_name, mode)

    # Load province map image
    image_path = input_file(map_name, "provinces.png")
    original_img = Image.open(image_path).convert("RGBA")

    img_data = original_img.load()
    width, height = original_img.size

    # Create a new transparent image
    new_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    new_img_data = new_img.load()

    # Process provinces (handle islands)
    visited_pixels = set()
    for y in range(height):
        for x in range(width):
            pixel_color = img_data[x, y][:3]
            if pixel_color in province_to_color and (x, y) not in visited_pixels:
                target_color = province_to_color[pixel_color]
                flood_fill(
                    x, y,
                    pixel_color,
                    target_color,
                    visited_pixels,
                    img_data,
                    new_img_data,
                    width,
                    height
                )

    # Paint borders
    new_img_data = paint_borders(True, True, new_img_data, width, height)

    # Apply overrides
    visited_pixels.clear()
    for y in range(height):
        for x in range(width):
            pixel_color = img_data[x, y][:3]
            if pixel_color in overrides and (x, y) not in visited_pixels:
                override_color = overrides[pixel_color]
                flood_fill(
                    x, y,
                    pixel_color,
                    override_color,
                    visited_pixels,
                    new_img_data,
                    new_img_data,
                    width,
                    height
                )

    # Save output
    output_path = os.path.join(
        os.path.dirname(input_file(map_name, "dummy")),
        "..", "..", "output", map_name, "maps", f"{filename}.png"
    )
    output_path = os.path.abspath(output_path)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    new_img.save(output_path, "PNG")

    print(f"🗺️ Map generated for '{map_name}' → {output_path}")