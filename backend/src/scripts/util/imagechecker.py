from PIL import Image
import os

provinces_cache = None
image_cache = None

def find_province(x, y):
    global provinces_cache, image_cache

    if provinces_cache is None:
        from ..loader.provinces import load_provinces
        provinces_cache = load_provinces()

    if image_cache is None:
        provinces_path = os.path.join(os.path.dirname(__file__), "..", "..", "input", "provinces.png")
        image_cache = Image.open(provinces_path)

    pixel_color = image_cache.getpixel((x, y))
    if len(pixel_color) == 4:
        pixel_color = pixel_color[:3]

    return provinces_cache.get(pixel_color, 0)

