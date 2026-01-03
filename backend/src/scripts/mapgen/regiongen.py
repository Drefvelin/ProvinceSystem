from PIL import Image, ImageEnhance
import os

from ..util.border_paint import paint_borders
from ..util.colour_mapping import build_color_mapping, get_color_overrides
from ..util.queue import load_queue, compile_queue, clear_mode
from ..util.dirs import input_file, validate_map


def sanitize_filename(color):
    return "_".join(map(str, color))


def generate_regions(map_name: str, mode: str, borders: bool, queued_regen: bool = False):
    validate_map(map_name)

    # -------------------------------------------------
    # Load base province map
    # -------------------------------------------------
    image_path = input_file(map_name, "provinces.png")
    base_img = Image.open(image_path).convert("RGBA")
    img_data = base_img.load()
    width, height = base_img.size

    # -------------------------------------------------
    # Build mappings
    # -------------------------------------------------
    province_to_color = build_color_mapping(map_name, mode)
    overrides = get_color_overrides(map_name, mode)

    # -------------------------------------------------
    # Output folder
    # -------------------------------------------------
    output_folder = os.path.abspath(
        os.path.join(
            os.path.dirname(image_path),
            "..", "..", "output", map_name, "regions", mode
        )
    )
    os.makedirs(output_folder, exist_ok=True)

    # -------------------------------------------------
    # Queue handling
    # -------------------------------------------------
    queued = None
    if queued_regen:
        compile_queue(map_name)
        queued = set(load_queue(map_name, mode))

        for fn in os.listdir(output_folder):
            base = fn.replace("_hover", "").replace("_nested", "").replace(".png", "")
            if base in queued:
                os.remove(os.path.join(output_folder, fn))
    else:
        for fn in os.listdir(output_folder):
            os.remove(os.path.join(output_folder, fn))

    # -------------------------------------------------
    # Pre-group all pixels by province color
    # -------------------------------------------------
    province_pixels = {}
    for y in range(height):
        for x in range(width):
            rgb = img_data[x, y][:3]
            if rgb in province_to_color:
                province_pixels.setdefault(rgb, []).append((x, y))

    # -------------------------------------------------
    # In-memory region images
    # -------------------------------------------------
    region_imgs = {}
    region_data = {}

    def get_region(color):
        img = region_imgs.get(color)
        if img is None:
            img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            region_imgs[color] = img
            region_data[color] = img.load()
        return region_data[color]

    # -------------------------------------------------
    # Paint provinces into regions
    # -------------------------------------------------
    for prov_rgb, pixels in province_pixels.items():
        color = province_to_color[prov_rgb]
        name = sanitize_filename(color)

        if queued is not None and name not in queued:
            continue

        data = get_region(color)
        for x, y in pixels:
            data[x, y] = (*color, 255)

        # --- overlord handling (nation mode only) ---
        if color in overrides:
            ocolor = overrides[color]
            odata = get_region(ocolor)
            for x, y in pixels:
                odata[x, y] = (*ocolor, 255)

    # -------------------------------------------------
    # Save region images (ONCE, FAST)
    # -------------------------------------------------
    for color, img in region_imgs.items():
        name = sanitize_filename(color)
        path = os.path.join(output_folder, f"{name}.png")
        img.save(path, "PNG")

    # -------------------------------------------------
    # Hover images
    # -------------------------------------------------
    for color in region_imgs:
        name = sanitize_filename(color)
        base = os.path.join(output_folder, f"{name}.png")
        hover = os.path.join(output_folder, f"{name}_hover.png")

        if queued is not None and name not in queued:
            continue

        img = Image.open(base).convert("RGBA")
        ImageEnhance.Brightness(img).enhance(1.4).save(
            hover, "PNG"
        )

    # -------------------------------------------------
    # Borders
    # -------------------------------------------------
    if borders:
        for color in region_imgs:
            name = sanitize_filename(color)

            if queued is not None and name not in queued:
                continue

            path = os.path.join(output_folder, f"{name}.png")
            img = Image.open(path).convert("RGBA")
            paint_borders(True, False, img.load(), width, height)
            img.save(path, "PNG")

    if queued_regen:
        clear_mode(map_name, mode)