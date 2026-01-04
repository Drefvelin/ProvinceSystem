from PIL import Image, ImageEnhance
import os

from ..util.border_paint import compute_border_owners, apply_region_borders
from ..util.colour_mapping import build_color_mapping, get_color_overrides
from ..util.queue import load_queue, compile_queue, clear_mode
from ..util.dirs import input_file, validate_map
import sys
import time

def log_progress(message):
    sys.stdout.write("\r" + message)
    sys.stdout.flush()


def sanitize_filename(color):
    return "_".join(map(str, color))


def generate_regions(map_name: str, mode: str, borders: bool, queued_regen: bool = False):
    validate_map(map_name)

    image_path = input_file(map_name, "provinces.png")
    base_img = Image.open(image_path).convert("RGBA")
    src = base_img.load()
    width, height = base_img.size

    province_to_color = build_color_mapping(map_name, mode)
    trade_mixed = getattr(build_color_mapping, "trade_mixed", None)
    overrides = get_color_overrides(map_name, mode)

    output_folder = os.path.abspath(
        os.path.join(
            os.path.dirname(image_path),
            "..", "..", "output", map_name, "regions", mode
        )
    )
    os.makedirs(output_folder, exist_ok=True)

    queued = None
    if queued_regen:
        compile_queue(map_name)
        queued = set(load_queue(map_name, mode))
        for fn in os.listdir(output_folder):
            base = fn.replace("_hover", "").replace(".png", "")
            if base in queued:
                os.remove(os.path.join(output_folder, fn))
    else:
        for fn in os.listdir(output_folder):
            os.remove(os.path.join(output_folder, fn))

    province_pixels = {}
    total_pixels = width * height
    processed = 0
    last_update = time.time()

    for y in range(height):
        for x in range(width):
            rgb = src[x, y][:3]
            if rgb in province_to_color:
                province_pixels.setdefault(rgb, []).append((x, y))

            processed += 1
            if time.time() - last_update > 0.1:  # update every 100ms
                percent = (processed / total_pixels) * 100
                log_progress(
                    f"Scanning pixels: {processed:,}/{total_pixels:,} "
                    f"({percent:5.1f}%)"
                )
                last_update = time.time()

    print()  # move to next line after loop

    region_imgs = {}
    region_data = {}

    def get_region(color_key):
        if color_key not in region_imgs:
            img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            region_imgs[color_key] = img
            region_data[color_key] = img.load()
        return region_data[color_key]

    total_regions = len(province_pixels)
    current_region = 0

    for prov_rgb, pixels in province_pixels.items():
        current_region += 1

        dominant_color = province_to_color[prov_rgb]
        name = sanitize_filename(dominant_color)

        log_progress(
            f"Building regions: {current_region}/{total_regions} "
            f"({(current_region/total_regions)*100:5.1f}%) "
            f"→ {name}"
        )

        if queued is not None and name not in queued:
            continue

        data = get_region(dominant_color)

        paint_rgb = dominant_color
        if trade_mixed is not None:
            paint_rgb = trade_mixed.get(prov_rgb, dominant_color)

        pr, pg, pb = paint_rgb
        for x, y in pixels:
            data[x, y] = (pr, pg, pb, 255)

        if dominant_color in overrides:
            ocolor = overrides[dominant_color]
            odata = get_region(ocolor)
            or_, og_, ob_ = ocolor
            for x, y in pixels:
                odata[x, y] = (or_, og_, ob_, 255)
    print()
    border_owners = None
    if borders and region_imgs:
        ref_img = next(iter(region_imgs.values()))
        border_owners = compute_border_owners(ref_img.load(), width, height)

        for color_key, img in region_imgs.items():
            apply_region_borders(
                img.load(),
                color_key,
                border_owners,
                width,
                height
            )

    total_outputs = len(region_imgs)

    for i, (color_key, img) in enumerate(region_imgs.items(), start=1):
        name = sanitize_filename(color_key)
        log_progress(
            f"Saving images: {i}/{total_outputs} "
            f"({(i/total_outputs)*100:5.1f}%)"
        )
        img.save(os.path.join(output_folder, f"{name}.png"), "PNG")
        img.close()

    print()

    for color_key in region_imgs:
        name = sanitize_filename(color_key)
        if queued is not None and name not in queued:
            continue

        base = os.path.join(output_folder, f"{name}.png")
        hover = os.path.join(output_folder, f"{name}_hover.png")

        img = Image.open(base).convert("RGBA")
        img = ImageEnhance.Brightness(img).enhance(1.25)
        img = ImageEnhance.Contrast(img).enhance(1.12)
        img.save(hover, "PNG")
        img.close()

    if queued_regen:
        clear_mode(map_name, mode)
