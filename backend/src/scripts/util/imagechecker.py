import json
from PIL import Image

# Load the counties from the counties.json file
with open("counties.json", "r") as file:
    counties_data = json.load(file)

# Load the duchies from the duchies.json file
with open("duchies.json", "r") as file:
    duchies_data = json.load(file)

# Load the provinces from the file into a dictionary for easy lookup
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
        provinces[rgb_values] = int(province_id.strip())

# Open the image
image = Image.open("provinces.png")

# Get pixel color at specific coordinates
x, y = 1827, 2294  # Example coordinates, change as necessary
pixel_color = image.getpixel((x, y))

# If the pixel has an alpha channel, remove it (use only the first three values)
if len(pixel_color) == 4:  # RGBA
    pixel_color = pixel_color[:3]  # Keep only RGB

# Print the RGB value of the pixel
print(f"Pixel RGB Color: {pixel_color}")

# Check if the pixel color matches any of the province colors
if pixel_color in provinces:
    province_id = provinces[pixel_color]
    print(f"Found province with the id {province_id}")
    
    # Now find which county this province belongs to
    county_id = None
    for county_id, county_data in counties_data.items():
        if province_id in county_data["provinces"]:
            print(f"Province {province_id} belongs to county: {county_id}")
            break

    if county_id:
        # Now find which duchy this county belongs to
        for duchy_name, duchy_data in duchies_data.items():
            if county_id in duchy_data["counties"]:
                print(f"County {county_id} belongs to duchy: {duchy_data['name']}")
                break
else:
    print("No matching province found.")

