from PIL import Image, ImageDraw, ImageFont
import numpy as np
from skimage.measure import label, regionprops

# Step 1: Load the painted image
image_path = "painted_map.png"  # Replace with your actual file path
img = Image.open(image_path)

# Convert to RGB if necessary
img_rgb = img.convert("RGB")
img_data = img_rgb.load()

# Step 2: Create a binary mask for the painted areas
painted_area_mask = np.zeros((img.height, img.width), dtype=np.uint8)

# Replace with the color of the painted area
for y in range(img.height):
    for x in range(img.width):
        if img_data[x, y] == (127, 14, 14):  # The color of painted areas
            painted_area_mask[y, x] = 1

# Step 3: Use connected component labeling to identify connected territories
labeled_mask = label(painted_area_mask)
regions = regionprops(labeled_mask)

# Step 4: Find the largest region (territory)
largest_region = max(regions, key=lambda r: r.area)

# Get the bounding box of the largest region
min_x, min_y, max_x, max_y = largest_region.bbox

# Step 5: Define the text you want to place
text = "Revenor"

# Step 6: Create a drawing object
draw = ImageDraw.Draw(img_rgb)

# Step 7: Try to use a basic font (you can replace it with a custom font if needed)
try:
    font = ImageFont.truetype("impact.ttf", 30)  # You may need to provide the correct path to the font
except IOError:
    font = ImageFont.load_default()  # Use the default font if the custom one fails

# Step 8: Calculate the size of the text
bbox = draw.textbbox((0, 0), text, font=font)
text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

# Step 9: Scale the font size to fit the bounding box of the largest region
scale_factor = min((max_x - min_x) / text_width, (max_y - min_y) / text_height) * 0.8  # 80% of the available space
scaled_font_size = int(30 * scale_factor)  # Adjust base font size

# Recreate the font with the new size
font = ImageFont.truetype("impact.ttf", scaled_font_size)

# Step 10: Calculate the position to center the text within the bounding box
bbox = draw.textbbox((0, 0), text, font=font)
text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
text_x = min_x + (max_x - min_x - text_width) // 2
text_y = min_y + (max_y - min_y - text_height) // 2

# Step 11: Create a temporary image to draw the text on it
text_img = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
text_draw = ImageDraw.Draw(text_img)

# Step 12: Function to draw text with a border (shadow effect)
def draw_text_with_border(draw, text, position, font, text_color, border_color):
    x, y = position
    # Draw the border (black or any other color) first with slight offsets
    border_offset = 2
    for dx in range(-border_offset, border_offset + 1):
        for dy in range(-border_offset, border_offset + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=border_color)
    
    # Then draw the main text over it
    draw.text((x, y), text, font=font, fill=text_color)

# Step 13: Draw the text with a black border and grey fill on the temporary image
draw_text_with_border(text_draw, text, (0, 0), font, text_color=(169, 169, 169), border_color=(0, 0, 0))

# Step 14: Rotate the text image (only the text)
rotation_angle = 25  # You can change this angle as needed
rotated_text_img = text_img.rotate(rotation_angle, expand=True, resample=Image.BICUBIC)

# Step 15: Calculate the position to paste the rotated text onto the original image
rotated_text_width, rotated_text_height = rotated_text_img.size
text_x = min_x + (max_x - min_x - rotated_text_width) // 2
text_y = min_y + (max_y - min_y - rotated_text_height) // 2

# Step 16: Paste the rotated text onto the original image
img_rgb.paste(rotated_text_img, (text_x, text_y), rotated_text_img)

# Step 17: Save the result
new_image_path = "painted_map_with_rotated_text.png"
img_rgb.save(new_image_path)

print(f"New image with rotated text saved as {new_image_path}")
