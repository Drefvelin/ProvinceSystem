from PIL import Image
import os

from ..util.dirs import input_file, validate_map

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
    patterns: list,
    scale_factor: int = 10
):
    validate_map(map_name)

    input_patterns_dir = input_file(map_name, "banner")
    output_banners_dir = os.path.join(
        os.path.dirname(input_file(map_name, "dummy")),
        "..", "..", "output", map_name, "banners"
    )
    output_banners_dir = os.path.abspath(output_banners_dir)

    os.makedirs(output_banners_dir, exist_ok=True)

    base_width, base_height = 20, 40
    width, height = base_width * scale_factor, base_height * scale_factor

    new_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    new_img_data = new_img.load()

    for entry in patterns:
        color, pattern = entry.split(".", 1)
        color = color.lower()
        pattern = pattern.lower().removeprefix("tfmc:")

        pattern_path = os.path.join(input_patterns_dir, f"{pattern}.png")

        if not os.path.isfile(pattern_path):
            print(f"⚠️ Pattern not found: {pattern}")
            continue

        dye_rgb = minecraft_dye_colors.get(color, (255, 255, 255))
        pattern_img = Image.open(pattern_path).convert("RGBA").load()

        for y in range(base_height):
            for x in range(base_width):
                px = pattern_img[x + 1, y + 1]
                if px[3] == 0:
                    continue

                intensity = px[0] / 255.0
                r = int(dye_rgb[0] * intensity)
                g = int(dye_rgb[1] * intensity)
                b = int(dye_rgb[2] * intensity)

                for dy in range(scale_factor):
                    for dx in range(scale_factor):
                        new_img_data[
                            x * scale_factor + dx,
                            y * scale_factor + dy
                        ] = (r, g, b)

    output_path = os.path.join(output_banners_dir, f"{banner_id}.png")
    new_img.save(output_path, "PNG")