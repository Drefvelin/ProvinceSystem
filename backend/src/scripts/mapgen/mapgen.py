from PIL import Image
import os
from ..util.colour_mapping import build_color_mapping
from ..util.border_paint import paint_borders
from ..util.flood_fill import flood_fill
from ..util.colour_mapping import get_color_overrides


def create_map(mode, filename, frontend_save):
    # Create a lookup dictionary for province color -> kingdom color
    province_to_color = build_color_mapping(mode)
    overrides = get_color_overrides(mode)

    # Open the original province map image
    image_path = os.path.join(os.path.dirname(__file__), "..", "..", "input", "provinces.png")
    original_img = Image.open(image_path).convert("RGBA")
    img_data = original_img.load()
    width, height = original_img.size

    # Create a new blank image with transparency
    new_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    new_img_data = new_img.load()

    # Process each province separately to handle islands
    visited_pixels = set()
    for y in range(height):
        for x in range(width):
            pixel_color = img_data[x, y][:3]
            if pixel_color in province_to_color and (x, y) not in visited_pixels:
                kingdom_color = province_to_color[pixel_color]
                flood_fill(x, y, pixel_color, kingdom_color, visited_pixels, img_data, new_img_data, width, height)

    if frontend_save:
        frontend_image_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "frontend", "public", "data", f"{filename}.png")
        new_img.save(frontend_image_path, "PNG")
        print(f"New image generated for the frontend and saved as {frontend_image_path}")

    new_img_data = paint_borders(True, True, new_img_data, width, height)

    visited_pixels = set()
    for y in range(height):
        for x in range(width):
            pixel_color = img_data[x, y][:3]
            if pixel_color in overrides and (x, y) not in visited_pixels:
                color = overrides[pixel_color]
                flood_fill(x, y, pixel_color, color, visited_pixels, new_img_data, new_img_data, width, height)

    # Save the new image
    new_image_path = os.path.join(os.path.dirname(__file__), "..", "..", "output", "maps", f"{filename}.png")
    new_img.save(new_image_path, "PNG")

    print(f"New image generated for the backend and saved as {new_image_path}")
