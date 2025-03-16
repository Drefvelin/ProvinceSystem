import re

def hex_to_rgb(hex_code):
    """Convert hex color code to RGB tuple."""
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def get_existing_colors(file_path):
    """Retrieve all existing RGB values from the file."""
    existing_colors = set()
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            match = re.match(r'^(\d+)\s*=\s*(\d+),(\d+),(\d+)', line.strip())
            if match:
                rgb = (int(match.group(2)), int(match.group(3)), int(match.group(4)))
                existing_colors.add(rgb)
    return existing_colors

def get_next_id(file_path):
    """Find the next available ID in the file."""
    highest_id = 0
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            match = re.match(r'^(\d+)\s*=\s*(\d+,\d+,\d+)', line.strip())
            if match:
                highest_id = max(highest_id, int(match.group(1)))
    return highest_id + 1

def add_color_to_file(file_path, hex_code):
    """Append the new color with the correct ID to the file, if it does not already exist."""
    rgb = hex_to_rgb(hex_code)
    existing_colors = get_existing_colors(file_path)
    
    if rgb in existing_colors:
        print("\033[91mColour already exists\033[0m")  # Prints in red
        return
    
    next_id = get_next_id(file_path)
    new_line = f"{next_id} = {rgb[0]},{rgb[1]},{rgb[2]}\n"
    
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(new_line)
    
    print(f"Added: {new_line.strip()}")

# Continuous input loop
file_path = 'provinces.txt'  # Change this if needed
while True:
    hex_code = input("Enter hex code (or type 'stop' to exit): ")
    if hex_code.lower() == 'stop':
        break
    add_color_to_file(file_path, hex_code)