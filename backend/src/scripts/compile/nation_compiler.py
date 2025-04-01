from ..loader.nations import load_nations
from ..bannergen.bannergen import create_banner
from ..bannergen.randombanner import generate_random_banner
from PIL import Image
import json
import os
import re

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "defines")

def clean_name(name: str) -> str:
    # Remove Minecraft color codes (e.g. §f, §c)
    name = re.sub(r"§.", "", name)
    # Remove hex codes like #ffffff
    name = re.sub(r"#(?:[0-9a-fA-F]{6})", "", name)
    return name.strip()

def clean_banner_patterns(patterns: list) -> list:
    return [pattern.replace("tfmc:", "") for pattern in patterns]

def process_nations():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    nations = load_nations()

    banner_folder = os.path.join(os.path.dirname(__file__), "..", "..", "output", "banner", "nation")
    os.makedirs(banner_folder, exist_ok=True)
    for file_name in os.listdir(banner_folder):
        file_path = os.path.join(banner_folder, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Initialize "subjects" field
    for nation_id, data in nations.items():
        if not isinstance(data, dict):
            print(f"⚠️ Skipping invalid nation entry: {nation_id} (value: {data})")
            continue
        data.setdefault("subjects", [])

        # If the nation has an overlord, add it to the overlord's "subjects" list
        if "overlord" in data:
            overlord_id = data["overlord"]
            if overlord_id in nations and isinstance(nations[overlord_id], dict):
                nations[overlord_id].setdefault("subjects", []).append(nation_id)
        
        # Inside the for nation_id, data in nations.items():
        data["name"] = clean_name(data.get("name", ""))

        if "banner" not in data:
            data["banner"] = generate_random_banner()

        # Sanitize patterns
        if "banner patterns" in data:
            data["banner patterns"] = clean_banner_patterns(data["banner patterns"])

    # Recursive function to calculate size (provinces + subjects' provinces)
    def calculate_size(nation_id):
        nation = nations[nation_id]
        total_size = len(nation.get("provinces", []))  # Own provinces
        subject_size = 0

        # Add sizes of all subjects
        for subject_id in nation.get("subjects", []):
            subject_size += calculate_size(subject_id)
            total_size += subject_size

        # Store computed size in the nation
        nation["size"] = total_size
        nation["subject_size"] = subject_size
        return total_size

    # Compute sizes for all nations
    for nation_id in nations:
        if "size" not in nations[nation_id]:  # Avoid redundant calculations
            calculate_size(nation_id)
        nation = nations[nation_id]
        if "banner" not in nation:
            nation["banner"] = generate_random_banner()
        rgb = nation["rgb"].split(',')
        id = rgb[0]+"_"+rgb[1]+"_"+rgb[2]
        create_banner("nation", id, nation["banner"])
        nation["banner"] = id
    
    if True:
        DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "frontend", "public", "data", "banners", "nation")
        os.makedirs(DIR, exist_ok=True)
        for file_name in os.listdir(DIR):
            file_path = os.path.join(DIR, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
        for file_name in os.listdir(banner_folder):
            new_image_path = os.path.join(banner_folder, file_name)
            if os.path.exists(new_image_path):
                new_img = Image.open(new_image_path).convert("RGBA")
                frontend_image_path = os.path.join(DIR, f"{file_name}")
                new_img.save(frontend_image_path, "PNG")
                print(f"Banner copied for the frontend and saved as {frontend_image_path}")
            else:
                print(f"Warning: {new_image_path} not found for frontend copy.")

    # Save modified JSON
    with open(os.path.join(OUTPUT_DIR, "nation.json"), "w", encoding="utf-8") as file:
        json.dump(nations, file, indent=4)