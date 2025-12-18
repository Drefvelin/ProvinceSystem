from PIL import Image
import os

from .dirs import (
    input_file,
    validate_map
)

# Per-map caches
_provinces_cache: dict[str, dict] = {}
_image_cache: dict[str, Image.Image] = {}


def find_province(map_name: str, x: int, y: int) -> int:
    """
    Returns province ID at (x, y) for the given map.
    Returns 0 if no province is found.
    """
    validate_map(map_name)

    # Load provinces data if not cached
    if map_name not in _provinces_cache:
        from ..loader.provinces import load_provinces
        _provinces_cache[map_name] = load_provinces(map_name)

    # Load province mask image if not cached
    if map_name not in _image_cache:
        provinces_path = input_file(map_name, "provinces.png")

        if not os.path.exists(provinces_path):
            raise FileNotFoundError(f"provinces.png not found for map '{map_name}'")

        _image_cache[map_name] = Image.open(provinces_path).convert("RGB")

    image = _image_cache[map_name]
    provinces = _provinces_cache[map_name]

    # Bounds check (important for safety)
    if x < 0 or y < 0 or x >= image.width or y >= image.height:
        return 0

    pixel_color = image.getpixel((x, y))  # (R, G, B)

    return provinces.get(pixel_color, 0)