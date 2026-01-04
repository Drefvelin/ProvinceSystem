from PIL import Image
import os
import sys
import time

from ..util.colour_mapping import build_color_mapping, get_color_overrides
from ..util.border_paint import paint_borders
from ..util.dirs import input_file, validate_map


def log_progress(message):
    sys.stdout.write("\r" + message)
    sys.stdout.flush()


def create_map(map_name: str, mode: str, filename: str):
    create_map(map_name, mode, filename, True)


def create_map(map_name: str, mode: str, filename: str, borders: bool):
    start_time = time.perf_counter()

    validate_map(map_name)

    province_to_color = build_color_mapping(map_name, mode)

    base_img = Image.open(input_file(map_name, "provinces.png")).convert("RGBA")
    width, height = base_img.size

    # --------------------------------------------------------------
    # Empty mapping → still generate transparent output
    # --------------------------------------------------------------
    if not province_to_color:
        out = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        output_path = os.path.abspath(
            os.path.join(
                os.path.dirname(input_file(map_name, "dummy")),
                "..", "..", "output", map_name, "maps", f"{filename}.png"
            )
        )
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        out.save(output_path, "PNG")

        elapsed = time.perf_counter() - start_time
        print(
            f"🗺️ Empty map generated for '{map_name}' (no mapping) "
            f"in {elapsed:.2f}s → {output_path}"
        )
        return

    overrides = get_color_overrides(map_name, mode)
    src = base_img.load()

    out = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    dst = out.load()

    # --------------------------------------------------------------
    # Paint map pixels with progress logging
    # --------------------------------------------------------------
    total_pixels = width * height
    processed = 0
    last_update = time.time()

    if overrides:
        for y in range(height):
            for x in range(width):
                rgb = src[x, y][:3]
                color = province_to_color.get(rgb)
                if color:
                    color = overrides.get(color, color)
                    dst[x, y] = (*color, 255)

                processed += 1
                if time.time() - last_update > 0.1:
                    percent = (processed / total_pixels) * 100
                    log_progress(
                        f"Painting map: {processed:,}/{total_pixels:,} "
                        f"({percent:5.1f}%)"
                    )
                    last_update = time.time()
    else:
        for y in range(height):
            for x in range(width):
                color = province_to_color.get(src[x, y][:3])
                if color:
                    dst[x, y] = (*color, 255)

                processed += 1
                if time.time() - last_update > 0.1:
                    percent = (processed / total_pixels) * 100
                    log_progress(
                        f"Painting map: {processed:,}/{total_pixels:,} "
                        f"({percent:5.1f}%)"
                    )
                    last_update = time.time()

    print()  # move to next line after progress output

    # --------------------------------------------------------------
    # Borders
    # --------------------------------------------------------------
    if borders:
        paint_borders(True, True, dst, width, height)

    # --------------------------------------------------------------
    # Save output
    # --------------------------------------------------------------
    output_path = os.path.abspath(
        os.path.join(
            os.path.dirname(input_file(map_name, "dummy")),
            "..", "..", "output", map_name, "maps", f"{filename}.png"
        )
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    out.save(output_path, "PNG")

    elapsed = time.perf_counter() - start_time
    print(
        f"🗺️ Map generated for '{map_name}' "
        f"(mode: {mode}) in {elapsed:.2f}s → {output_path}"
    )