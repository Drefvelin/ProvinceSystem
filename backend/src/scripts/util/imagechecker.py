from PIL import Image
from ..loader.provinces import load_provinces
import os

def get_province(x, y):

    provinces = load_provinces()

    # Open the image
    provinces_path = os.path.join(os.path.dirname(__file__), "..", "..", "input", "provinces.png")
    image = Image.open(provinces_path)

    # Get pixel color at specific coordinates
    pixel_color = image.getpixel((x, y))

    # If the pixel has an alpha channel, remove it (use only the first three values)
    if len(pixel_color) == 4:  # RGBA
        pixel_color = pixel_color[:3]  # Keep only RGB

    # Print the RGB value of the pixel
    print(f"Pixel RGB Color: {pixel_color}")

    # Check if the pixel color matches any of the province colors
    if pixel_color in provinces:
        province_id = provinces[pixel_color]
        return province_id
    else:
        return 0

