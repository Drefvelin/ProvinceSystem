from PIL import Image, ImageEnhance
import os
from ..util.border_paint import paint_borders
from ..util.flood_fill import flood_fill
from ..util.colour_mapping import build_color_mapping

def sanitize_filename(color_tuple):
    """
    Converts an RGB tuple to a safe filename (e.g., (255, 0, 0) -> "255_0_0").
    """
    return "_".join(map(str, color_tuple)).replace("(", "").replace(")", "").replace(",", "").replace(" ", "")

def draw(x, y, new_img, new_image_path, pixel_color, province_to_color, visited_pixels, img_data, width, height, painted_colour):
    """
    Fills and saves an image for a region.
    """
    try:
        new_img_data = new_img.load()
        color = province_to_color[pixel_color]
        flood_fill(x, y, pixel_color, color, visited_pixels, img_data, new_img_data, width, height)

        painted_colour.add(province_to_color[pixel_color])
        new_img.save(new_image_path, "PNG")
    except Exception as e:
        print(f"Error saving {new_image_path}: {e}")

def lighten_image(image_path, hover_image_path):
    """
    Opens an image, increases brightness, and saves it as a hover version.
    """
    try:
        img = Image.open(image_path).convert("RGBA")
        enhancer = ImageEnhance.Brightness(img)
        lighter_img = enhancer.enhance(1.4)  # Increase brightness by 40%
        lighter_img.save(hover_image_path, "PNG")
        print(f"Hover image created: {hover_image_path}")
    except Exception as e:
        print(f"Error generating hover image {hover_image_path}: {e}")

def generate_regions(mode, borders):
    """
    Generate separate images for each region (county, duchy, kingdom).
    """
    # Load province map
    image_path = os.path.join(os.path.dirname(__file__), "..", "..", "input", "provinces.png")
    original_img = Image.open(image_path).convert("RGBA")
    img_data = original_img.load()
    width, height = original_img.size

    # Load color mappings for mode (county, duchy, kingdom)
    province_to_color = build_color_mapping(mode)

    # Create output folder
    output_folder = os.path.join(os.path.dirname(__file__), "..", "..", "output", "regions", mode)
    os.makedirs(output_folder, exist_ok=True)

    painted_colour = set()
    visited_pixels = set()

    # === STEP 1: Generate normal images ===
    for y in range(height):
        for x in range(width):
            pixel_color = img_data[x, y][:3]
            if pixel_color in province_to_color and (x, y) not in visited_pixels:
                color_code = province_to_color[pixel_color]
                filename = sanitize_filename(color_code) + ".png"
                new_image_path = os.path.join(output_folder, filename)

                if color_code not in painted_colour:
                    new_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))  # Transparent image
                    draw(x, y, new_img, new_image_path, pixel_color, province_to_color, visited_pixels, img_data, width, height, painted_colour)
                    painted_colour.add(color_code)
                    print(f"New image saved: {new_image_path}")
                else:
                    new_img = Image.open(new_image_path)
                    draw(x, y, new_img, new_image_path, pixel_color, province_to_color, visited_pixels, img_data, width, height, painted_colour)
                    print(f"Edited: {new_image_path}")

    # === STEP 2: Generate hover versions by lightening existing images ===
    for color in painted_colour:
        filename = sanitize_filename(color) + ".png"
        filename_hover = sanitize_filename(color) + "_hover.png"
        normal_image_path = os.path.join(output_folder, filename)
        hover_image_path = os.path.join(output_folder, filename_hover)

        if os.path.exists(normal_image_path):
            lighten_image(normal_image_path, hover_image_path)
        else:
            print(f"Warning: {normal_image_path} not found, hover version skipped.")

    # === STEP 3: Paint Borders ===
    if borders:
        for color in painted_colour:
            for i in range(2):  # Process both normal and hover images
                filename = sanitize_filename(color) + ("_hover.png" if i > 0 else ".png")
                new_image_path = os.path.join(output_folder, filename)

                if os.path.exists(new_image_path):
                    new_img = Image.open(new_image_path).convert("RGBA")
                    new_img_data = new_img.load()
                    paint_borders(True, False, new_img_data, width, height)
                    new_img.save(new_image_path, "PNG")
                    print(f"Borders painted for {new_image_path}")
                else:
                    print(f"Warning: {new_image_path} not found for border painting.")
