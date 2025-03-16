from PIL import Image

# Load the provinces from the provinces.txt file
province_file_path = "provinces.txt"
provinces = {}

# Read the provinces from the provinces.txt file
with open(province_file_path, "r") as file:
    for line in file:
        # Skip comments or empty lines
        if line.startswith("##") or not line.strip():
            continue
        # Split the line by " = " to get ID and RGB values
        province_id, rgb_values = line.split(" = ")
        rgb_values = tuple(map(int, rgb_values.split(",")))  # Convert to a tuple of integers
        provinces[rgb_values] = int(province_id.strip())  # Store the province ID with its RGB

# Open the image to be processed
image_path = "provinces.png"  # Input image path
img = Image.open(image_path)

# Convert image to RGB (in case it's RGBA or other format)
img_rgb = img.convert("RGB")

# Get the pixel data of the image
img_data = img_rgb.load()

# The new color to replace province colors with (155, 155, 0)
new_color = (127, 14, 14)
# The border color to use for the edges (255, 0, 0)
border_color = (5, 5, 5)

# First, paint the provinces
for y in range(img.height):
    for x in range(img.width):
        pixel_color = img_data[x, y]
        if pixel_color in provinces:  # If the pixel matches one of the province colors
            img_data[x, y] = new_color  # Replace with the new color

# Now, after all provinces are painted, paint the borders
# Create a set to store border pixels to avoid duplicates
borders = set()

border = True

# Iterate through all pixels and check if they're part of a painted province
if border:
    for y in range(img.height):
        for x in range(img.width):
            pixel_color = img_data[x, y]
            if pixel_color == new_color:  # Only check for borders in the painted province regions
                # Look at neighboring pixels: left, right, up, down
                neighbors = [
                    (x - 1, y),  # Left
                    (x + 1, y),  # Right
                    (x, y - 1),  # Up
                    (x, y + 1),  # Down
                ]
                for nx, ny in neighbors:
                    if 0 <= nx < img.width and 0 <= ny < img.height:
                        neighbor_color = img_data[nx, ny]
                        if neighbor_color != new_color and neighbor_color != border_color:  # If the neighbor is not the same color or border
                            # Add a square region around this border pixel to the borders set (3x3 or adjustable radius)
                            for dx in range(-5, 6):  # 3x3 area around the border pixel
                                for dy in range(-5, 6):
                                    nx2, ny2 = x + dx, y + dy
                                    if 0 <= nx2 < img.width and 0 <= ny2 < img.height:
                                        borders.add((nx2, ny2))
                            break

# Apply the border color (255, 0, 0) to all the border pixels
for border_pixel in borders:
    img_data[border_pixel] = border_color

# Save the new image
new_image_path = "painted_map.png"
img_rgb.save(new_image_path)

print(f"New image with borders saved as {new_image_path}")
