from PIL import Image
import os
import sys
import time

from ..util.border_paint import compute_border_owners, apply_region_borders
from ..util.colour_mapping import build_color_mapping, get_color_overrides
from ..util.queue import load_queue, compile_queue, clear_mode
from ..util.dirs import input_file, validate_map, map_image


def log_progress(message):
    sys.stdout.write("\r" + message)
    sys.stdout.flush()


def sanitize_filename(color):
    return "_".join(map(str, color))


def lighten_color(rgb):
    """
    Approximates:
      Brightness 1.25
      Contrast   1.12
    """
    r, g, b = rgb

    # brightness
    r = min(255, int(r * 1.25))
    g = min(255, int(g * 1.25))
    b = min(255, int(b * 1.25))

    # contrast around midpoint 128
    def contrast(c):
        return min(255, max(0, int((c - 128) * 1.12 + 128)))

    return contrast(r), contrast(g), contrast(b)


def generate_regions(map_name: str, mode: str, borders: bool, queued_regen: bool = False):
    start_time = time.perf_counter()
    validate_map(map_name)

    image_path = input_file(map_name, "provinces.png")
    base_img = Image.open(image_path).convert("RGBA")
    src = base_img.load()
    width, height = base_img.size

    province_to_color = build_color_mapping(map_name, mode)
    if not province_to_color:
        print(f"No region color mapping for mode '{mode}', skipping generation.")
        return
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

    # ------------------------------------------------------------------
    # Scan province pixels
    # ------------------------------------------------------------------

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
            if time.time() - last_update > 0.1:
                percent = (processed / total_pixels) * 100
                log_progress(
                    f"Scanning pixels: {processed:,}/{total_pixels:,} "
                    f"({percent:5.1f}%)"
                )
                last_update = time.time()

    print()

    # ------------------------------------------------------------------
    # Region buffers (base + hover)
    # ------------------------------------------------------------------

    region_imgs = {}
    region_data = {}
    light_cache = {}

    def get_region(color_key):
        if color_key not in region_imgs:
            base = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            hover = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            region_imgs[color_key] = (base, hover)
            region_data[color_key] = (base.load(), hover.load())
        return region_data[color_key]

    # ------------------------------------------------------------------
    # Paint regions (base + hover simultaneously)
    # ------------------------------------------------------------------

    total_regions = len(province_pixels)
    current_region = 0

    for prov_rgb, pixels in province_pixels.items():
        dominant_color = province_to_color[prov_rgb]
        name = sanitize_filename(dominant_color)

        if queued is not None and name not in queued:
            continue

        current_region += 1
        log_progress(
            f"Building regions: {current_region}/{total_regions} "
            f"({(current_region/total_regions)*100:5.1f}%) "
            f"→ {name}"
        )

        if dominant_color not in light_cache:
            light_cache[dominant_color] = lighten_color(dominant_color)

        paint_rgb = dominant_color
        if trade_mixed is not None:
            paint_rgb = trade_mixed.get(prov_rgb, dominant_color)

        pr, pg, pb = paint_rgb
        lr, lg, lb = light_cache[dominant_color]

        base_data, hover_data = get_region(dominant_color)

        for x, y in pixels:
            base_data[x, y] = (pr, pg, pb, 255)
            hover_data[x, y] = (lr, lg, lb, 255)

        # overrides
        if dominant_color in overrides:
            ocolor = overrides[dominant_color]
            if ocolor not in light_cache:
                light_cache[ocolor] = lighten_color(ocolor)

            or_, og_, ob_ = ocolor
            olr, olg, olb = light_cache[ocolor]

            obase, ohover = get_region(ocolor)

            for x, y in pixels:
                obase[x, y] = (or_, og_, ob_, 255)
                ohover[x, y] = (olr, olg, olb, 255)

    print()

    # ------------------------------------------------------------------
    # Borders (applied to both images)
    # ------------------------------------------------------------------

    if borders and region_imgs:
        ref_img = Image.open(map_image(map_name, mode)).convert("RGBA")
        border_owners = compute_border_owners(ref_img.load(), width, height)

        total_regions = len(region_imgs)
        for i, (color_key, (base, hover)) in enumerate(region_imgs.items(), start=1):
            log_progress(
                f"Painting borders: {i}/{total_regions} "
                f"({(i/total_regions)*100:5.1f}%)"
            )

            apply_region_borders(
                base.load(),
                color_key,
                border_owners,
                width,
                height
            )
            apply_region_borders(
                hover.load(),
                color_key,
                border_owners,
                width,
                height
            )

    print()

    # ------------------------------------------------------------------
    # Save outputs (single pass)
    # ------------------------------------------------------------------

    total_outputs = len(region_imgs)
    for i, (color_key, (base, hover)) in enumerate(region_imgs.items(), start=1):
        name = sanitize_filename(color_key)

        if queued is not None and name not in queued:
            continue

        log_progress(
            f"Saving images: {i}/{total_outputs} "
            f"({(i/total_outputs)*100:5.1f}%)"
        )

        base.save(os.path.join(output_folder, f"{name}.png"), "PNG")
        hover.save(os.path.join(output_folder, f"{name}_hover.png"), "PNG")

        base.close()
        hover.close()

    print()

    if queued_regen:
        clear_mode(map_name, mode)
    end_time = time.perf_counter()
    elapsed = end_time - start_time

    print(
        f"Region generation for mode '{mode}' "
        f"took {elapsed:.2f} seconds"
    )

