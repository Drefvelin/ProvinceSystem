from PIL import Image
import os

from ..util.dirs import input_file, validate_map

# Minecraft dye colors (RGB)
minecraft_dye_colors = {
    "white":      (255, 255, 255),
    "orange":     (216, 127, 51),
    "magenta":    (178, 76, 216),
    "light_blue": (102, 153, 216),
    "yellow":     (229, 229, 51),
    "lime":       (127, 204, 25),
    "pink":       (242, 127, 165),
    "gray":       (76, 76, 76),
    "light_gray": (153, 153, 153),
    "cyan":       (76, 127, 153),
    "purple":     (127, 63, 178),
    "blue":       (51, 76, 178),
    "brown":      (102, 76, 51),
    "green":      (102, 127, 51),
    "red":        (153, 51, 51),
    "black":      (25, 25, 25),
}


def create_banner(
    map_name: str,
    mode: str,
    banner_id: str,
    patterns: list[str],
    scale_factor: int = 10
):
    """
    Generates a Minecraft-accurate banner image:
    - Uses alpha channel for gradients
    - Correctly layers patterns
    - Matches Java Edition banner rendering
    """
    validate_map(map_name)

    # Input / output paths
    input_patterns_dir = input_file(map_name, "banner")
    output_banners_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(input_file(map_name, "dummy")),
            "..", "..", "output", map_name, "banners", mode
        )
    )
    os.makedirs(output_banners_dir, exist_ok=True)

    # Minecraft banner base size (without pole)
    base_width, base_height = 20, 40
    width, height = base_width * scale_factor, base_height * scale_factor

    # Final banner image (RGBA)
    banner = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    banner_px = banner.load()

    for entry in patterns:
        try:
            color_name, pattern_name = entry.split(".", 1)
        except ValueError:
            print(f"⚠️ Invalid banner entry: {entry}")
            continue

        color_name = color_name.lower()
        pattern_name = pattern_name.lower().removeprefix("tfmc:")

        dye_rgb = minecraft_dye_colors.get(color_name)
        if not dye_rgb:
            print(f"⚠️ Unknown dye color: {color_name}")
            continue

        pattern_path = os.path.join(input_patterns_dir, f"{pattern_name}.png")
        if not os.path.isfile(pattern_path):
            print(f"⚠️ Pattern not found: {pattern_name}")
            continue

        pattern_img = Image.open(pattern_path).convert("RGBA")
        pattern_px = pattern_img.load()

        # --- APPLY PATTERN WITH TRUE MINECRAFT BLENDING ---
        for y in range(base_height):
            for x in range(base_width):
                # +1 offset = skip transparent border in MC textures
                pr, pg, pb, pa = pattern_px[x + 1, y + 1]
                if pa == 0:
                    continue

                alpha = pa / 255.0

                # Dye contribution
                dr = int(dye_rgb[0] * alpha)
                dg = int(dye_rgb[1] * alpha)
                db = int(dye_rgb[2] * alpha)

                for dy in range(scale_factor):
                    for dx in range(scale_factor):
                        px = x * scale_factor + dx
                        py = y * scale_factor + dy

                        # Existing pixel (layered blending)
                        er, eg, eb, ea = banner_px[px, py]

                        # Alpha compositing (source-over)
                        out_r = int(er * (1 - alpha) + dr)
                        out_g = int(eg * (1 - alpha) + dg)
                        out_b = int(eb * (1 - alpha) + db)

                        banner_px[px, py] = (out_r, out_g, out_b, 255)

    output_path = os.path.join(output_banners_dir, f"{banner_id}.png")
    banner.save(output_path, "PNG")