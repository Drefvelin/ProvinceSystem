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


def create_map(
    map_name: str,
    mode: str,
    filename: str,
    borders: bool = True,
    # IMPORTANT:
    # For frontend picking/canvas reference this MUST stay False,
    # otherwise vassals get overwritten by overlord colours and become un-pickable.
    # Pick maps must also keep raw nation rgb — never call display_colour.display_rgb here.
    apply_overrides: bool = False,
):
    """
    Creates a single full map image from provinces.png using the mapping for `mode`.

    - When apply_overrides=False (default): produces a *pick-safe* map where each region’s own RGB exists.
    - When apply_overrides=True: vassal pixels are replaced by their overlord colour.
    - Display muting for hover/drill overlays lives in regiongen.py only.
    """
    start_time = time.perf_counter()
    validate_map(map_name)

    province_to_color = build_color_mapping(map_name, mode)

    base_img = Image.open(input_file(map_name, "provinces.png")).convert("RGBA")
    src = base_img.load()
    width, height = base_img.size

    # --------------------------------------------------------------
    # Output path
    # --------------------------------------------------------------
    output_path = os.path.abspath(
        os.path.join(
            os.path.dirname(input_file(map_name, "dummy")),
            "..", "..", "output", map_name, "maps", f"{filename}.png"
        )
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # --------------------------------------------------------------
    # Empty mapping → transparent output
    # --------------------------------------------------------------
    if not province_to_color:
        out = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        out.save(output_path, "PNG")
        print(f"🗺️ Empty map generated → {output_path}")
        return

    overrides = get_color_overrides(map_name, mode) if apply_overrides else {}

    out = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    dst = out.load()

    # --------------------------------------------------------------
    # Paint map pixels
    # --------------------------------------------------------------
    total_pixels = width * height
    processed = 0
    last_update = time.time()

    if not overrides:
        # Fast path (pick-safe)
        for y in range(height):
            for x in range(width):
                color = province_to_color.get(src[x, y][:3])

                # 🚫 Skip null / sentinel colour
                if color and color != (0, 0, 0):
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
        # Override path (display-only)
        for y in range(height):
            for x in range(width):
                rgb = src[x, y][:3]
                color = province_to_color.get(rgb)

                if color:
                    color = overrides.get(color, color)

                    # 🚫 Skip null / sentinel colour
                    if color != (0, 0, 0):
                        dst[x, y] = (*color, 255)

                processed += 1
                if time.time() - last_update > 0.1:
                    percent = (processed / total_pixels) * 100
                    log_progress(
                        f"Painting map: {processed:,}/{total_pixels:,} "
                        f"({percent:5.1f}%)"
                    )
                    last_update = time.time()

    print()

    # --------------------------------------------------------------
    # Borders
    # --------------------------------------------------------------
    if borders:
        paint_borders(True, True, dst, width, height)

    # --------------------------------------------------------------
    # Save output
    # --------------------------------------------------------------
    out.save(output_path, "PNG")

    elapsed = time.perf_counter() - start_time
    print(
        f"🗺️ Map generated for '{map_name}' "
        f"(mode={mode}, borders={borders}, apply_overrides={apply_overrides}) "
        f"in {elapsed:.2f}s → {output_path}"
    )
