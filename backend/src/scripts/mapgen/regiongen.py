from PIL import Image, ImageEnhance
import os

from ..util.border_paint import paint_borders
from ..util.flood_fill import flood_fill
from ..util.colour_mapping import build_color_mapping, get_color_overrides
from ..util.queue import load_queue, compile_queue, clear_mode
from ..util.dirs import input_file, validate_map


def is_overlord(rgb_tuple, overrides):
    return rgb_tuple in overrides.values()


def sanitize_filename(color_tuple):
    return "_".join(map(str, color_tuple))


def draw(
    x, y,
    new_img,
    new_image_path,
    pixel_color,
    color,
    visited_pixels,
    img_data,
    width,
    height,
    painted_colour,
    overrides,
    output_folder,
    first
):
    try:
        new_img_data = new_img.load()
        flood_fill(x, y, pixel_color, color, visited_pixels, img_data, new_img_data, width, height)
        painted_colour.add(color)
        new_img.save(new_image_path, "PNG")

        if is_overlord(color, overrides) and first:
            nested_filename = sanitize_filename(color) + "_nested.png"
            nested_image_path = os.path.join(output_folder, nested_filename)

            nested_img = (
                Image.open(nested_image_path)
                if os.path.exists(nested_image_path)
                else Image.new("RGBA", (width, height), (0, 0, 0, 0))
            )

            nested_img_data = nested_img.load()
            flood_fill(x, y, pixel_color, color, set(), img_data, nested_img_data, width, height)
            nested_img.save(nested_image_path, "PNG")

        if color in overrides:
            overlord_color = overrides[color]
            overlord_filename = sanitize_filename(overlord_color) + ".png"
            overlord_image_path = os.path.join(output_folder, overlord_filename)

            overlord_img = (
                Image.open(overlord_image_path)
                if overlord_color in painted_colour
                else Image.new("RGBA", (width, height), (0, 0, 0, 0))
            )

            draw(
                x, y,
                overlord_img,
                overlord_image_path,
                pixel_color,
                overlord_color,
                set(),
                img_data,
                width,
                height,
                painted_colour,
                overrides,
                output_folder,
                False
            )

    except Exception as e:
        print(f"Error saving {new_image_path}: {e}")


def lighten_image(image_path, hover_image_path):
    try:
        img = Image.open(image_path).convert("RGBA")
        ImageEnhance.Brightness(img).enhance(1.4).save(hover_image_path, "PNG")
    except Exception as e:
        print(f"Error lightening image {hover_image_path}: {e}")


def generate_regions(map_name: str, mode: str, borders: bool, queued_regen: bool = False):
    validate_map(map_name)

    # === Load province map ===
    image_path = input_file(map_name, "provinces.png")
    original_img = Image.open(image_path).convert("RGBA")

    img_data = original_img.load()
    width, height = original_img.size

    # === Color mappings ===
    province_to_color = build_color_mapping(map_name, mode)
    overrides = get_color_overrides(map_name, mode)

    # === Output folder ===
    output_folder = os.path.abspath(
        os.path.join(
            os.path.dirname(image_path),
            "..", "..", "output", map_name, "regions", mode
        )
    )
    os.makedirs(output_folder, exist_ok=True)

    # === Handle queued regeneration ===
    queued = set()
    if queued_regen:
        compile_queue(map_name)
        queued = set(load_queue(map_name, mode))

        for file_name in os.listdir(output_folder):
            base = file_name.replace("_hover", "").replace("_nested", "")
            if base.endswith(".png"):
                base = base[:-4]
            if base in queued:
                os.remove(os.path.join(output_folder, file_name))
    else:
        for file_name in os.listdir(output_folder):
            os.remove(os.path.join(output_folder, file_name))

    painted_colour = set()
    visited_pixels = set()

    # === STEP 1: Base region images ===
    for y in range(height):
        for x in range(width):
            pixel_color = img_data[x, y][:3]

            if pixel_color in province_to_color and (x, y) not in visited_pixels:
                color_code = province_to_color[pixel_color]
                filename = sanitize_filename(color_code) + ".png"

                if queued_regen and sanitize_filename(color_code) not in queued:
                    continue

                new_image_path = os.path.join(output_folder, filename)

                img = (
                    Image.open(new_image_path)
                    if color_code in painted_colour
                    else Image.new("RGBA", (width, height), (0, 0, 0, 0))
                )

                draw(
                    x, y,
                    img,
                    new_image_path,
                    pixel_color,
                    color_code,
                    visited_pixels,
                    img_data,
                    width,
                    height,
                    painted_colour,
                    overrides,
                    output_folder,
                    True
                )

    # === STEP 2: Hover images ===
    for file_name in os.listdir(output_folder):
        if "_hover" in file_name:
            continue

        base, ext = os.path.splitext(file_name)
        hover_name = f"{base}_hover{ext}"

        if queued_regen and base.replace("_nested", "") not in queued:
            continue

        lighten_image(
            os.path.join(output_folder, file_name),
            os.path.join(output_folder, hover_name)
        )

    # === STEP 3: Borders ===
    if borders:
        for file_name in os.listdir(output_folder):
            base = file_name.replace("_hover", "").replace("_nested", "").replace(".png", "")
            if queued_regen and base not in queued:
                continue

            path = os.path.join(output_folder, file_name)
            img = Image.open(path).convert("RGBA")
            paint_borders(True, False, img.load(), width, height)
            img.save(path, "PNG")

    if queued_regen:
        clear_mode(map_name, mode)