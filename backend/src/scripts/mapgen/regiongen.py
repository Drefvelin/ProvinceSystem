from PIL import Image, ImageEnhance
import os
from ..util.border_paint import paint_borders
from ..util.flood_fill import flood_fill
from ..util.colour_mapping import build_color_mapping
from ..util.colour_mapping import get_color_overrides

def is_overlord(rgb_tuple, overrides):
    """
    Checks if a given RGB tuple is an overlord (i.e., appears as a value in the overrides dictionary).
    
    :param rgb_tuple: The RGB tuple to check (e.g., (255, 0, 0))
    :param overrides: The overrides dictionary mapping regions to their overlords.
    :return: True if the RGB tuple is an overlord, False otherwise.
    """
    return rgb_tuple in overrides.values()

def sanitize_filename(color_tuple):
    """
    Converts an RGB tuple to a safe filename (e.g., (255, 0, 0) -> "255_0_0").
    """
    return "_".join(map(str, color_tuple)).replace("(", "").replace(")", "").replace(",", "").replace(" ", "")

def draw(x, y, new_img, new_image_path, pixel_color, color, visited_pixels, img_data, width, height, painted_colour, overrides, output_folder, first):
    """
    Fills and saves an image for a region.
    """
    try:
        new_img_data = new_img.load()
        flood_fill(x, y, pixel_color, color, visited_pixels, img_data, new_img_data, width, height)
        painted_colour.add(color)
        new_img.save(new_image_path, "PNG")
        if is_overlord(color, overrides) and first:
            nested_filename = sanitize_filename(color) + "_nested.png"
            nested_image_path = os.path.join(output_folder, nested_filename)
            nested_img = None
            if not os.path.exists(nested_image_path):
                nested_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))  # Transparent image
                print(f"New overlord nested image saved: {nested_image_path}")
            else:
                nested_img = Image.open(nested_image_path)
                print(f"Edited nested Overlord: {nested_image_path}")
            nested_img_data = nested_img.load()
            flood_fill(x, y, pixel_color, color, set(), img_data, nested_img_data, width, height)
            nested_img.save(nested_image_path, "PNG")
        if color in overrides:
            overlord_color = overrides[color]
            overlord_filename = sanitize_filename(overlord_color) + ".png"
            overlord_image_path = os.path.join(output_folder, overlord_filename)
            if overlord_color not in painted_colour:
                overlord_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))  # Transparent image
                draw(x, y, overlord_img, overlord_image_path, pixel_color, overlord_color, set(), img_data, width, height, painted_colour, overrides, output_folder, False)
                print(f"New overlord image saved: {new_image_path}")
            else:
                overlord_img = Image.open(overlord_image_path)
                draw(x, y, overlord_img, overlord_image_path, pixel_color, overlord_color, set(), img_data, width, height, painted_colour, overrides, output_folder, False)
                print(f"Edited Overlord: {new_image_path}")

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
        print(f"Lightened image: {hover_image_path}")
    except Exception as e:
        print(f"Error lightening image {hover_image_path}: {e}")


def generate_regions(mode, borders, frontend_save, queued_regen=False):
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
    overrides = get_color_overrides(mode)

    # Create output folder
    output_folder = os.path.join(os.path.dirname(__file__), "..", "..", "output", "regions", mode)
    os.makedirs(output_folder, exist_ok=True)
    if queued_regen:
        from ..util.queue import load_queue, compile_queue
        compile_queue()
        queue = load_queue(mode)
        print(queue)
        queued = set(queue)
        for file_name in os.listdir(output_folder):
            base_name = file_name.replace("_hover", "").replace("_nested", "")
            if base_name.endswith(".png"):
                base_name = base_name[:-4]
            if base_name in queued:
                file_path = os.path.join(output_folder, file_name)
                try:
                    # Make sure to close any open file before removing
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except PermissionError:
                    print(f"Could not delete {file_path}. Is it open in another program?")
    else:
        for file_name in os.listdir(output_folder):
            file_path = os.path.join(output_folder, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

    painted_colour = set()
    visited_pixels = set()

    # === STEP 1: Generate normal images ===
    for y in range(height):
        for x in range(width):
            pixel_color = img_data[x, y][:3]
            if pixel_color in province_to_color and (x, y) not in visited_pixels:
                color_code = province_to_color[pixel_color]
                if queued_regen and sanitize_filename(color_code) not in queued:
                    continue
                filename = sanitize_filename(color_code) + ".png"
                new_image_path = os.path.join(output_folder, filename)

                if color_code not in painted_colour:
                    new_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))  # Transparent image
                    draw(x, y, new_img, new_image_path, pixel_color, color_code, visited_pixels, img_data, width, height, painted_colour, overrides, output_folder, True)
                    print(f"New image saved: {new_image_path}")
                    

                else:
                    new_img = Image.open(new_image_path)
                    draw(x, y, new_img, new_image_path, pixel_color, color_code, visited_pixels, img_data, width, height, painted_colour, overrides, output_folder, True)
                    print(f"Edited: {new_image_path}")

    # === STEP 2: Generate hover versions by lightening existing images ===
    for file_name in os.listdir(output_folder):
        # Skip already-hover files
        if "_hover" in file_name:
            continue

        # Split base and extension
        base_name, ext = os.path.splitext(file_name)

        # Determine hover filename
        if "_nested" in base_name:
            hover_filename = base_name + "_hover" + ext  # results in something like 255_0_0_nested_hover.png
        else:
            hover_filename = base_name + "_hover" + ext  # results in 255_0_0_hover.png

        if queued_regen and base_name not in queued and not base_name.replace("_nested", "") in queued:
            continue

        # Define paths
        normal_image_path = os.path.join(output_folder, file_name)
        hover_image_path = os.path.join(output_folder, hover_filename)

        if os.path.exists(normal_image_path) and ext.lower() in [".png", ".jpg", ".jpeg"]:
            lighten_image(normal_image_path, hover_image_path)
        else:
            print(f"Skipping non-image file: {normal_image_path}")



    # === STEP 3: Paint Borders ===
    if borders:
        for file_name in os.listdir(output_folder):
            new_image_path = os.path.join(output_folder, file_name)
            base_name, ext = os.path.splitext(file_name)
            clean_name = base_name.replace("_hover", "").replace("_nested", "")
            if queued_regen and clean_name not in queued:
                continue
            if os.path.exists(new_image_path):
                new_img = Image.open(new_image_path).convert("RGBA")
                new_img_data = new_img.load()
                paint_borders(True, False, new_img_data, width, height)
                new_img.save(new_image_path, "PNG")
                print(f"Borders painted for {new_image_path}")
            else:
                print(f"Warning: {new_image_path} not found for border painting.")
    if frontend_save:
        DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "frontend", "public", "data", "regions", f"{mode}")
        os.makedirs(DIR, exist_ok=True)
        for file_name in os.listdir(DIR):
            file_path = os.path.join(DIR, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
        for file_name in os.listdir(output_folder):
            new_image_path = os.path.join(output_folder, file_name)
            if os.path.exists(new_image_path):
                new_img = Image.open(new_image_path).convert("RGBA")
                new_img_data = new_img.load()
                frontend_image_path = os.path.join(DIR, f"{file_name}")
                new_img.save(frontend_image_path, "PNG")
                print(f"Region copied for the frontend and saved as {frontend_image_path}")
            else:
                print(f"Warning: {new_image_path} not found for frontend copy.")
    #if queued_regen:
    #    from ..util.queue import clear_mode
    #   clear_mode(mode)
