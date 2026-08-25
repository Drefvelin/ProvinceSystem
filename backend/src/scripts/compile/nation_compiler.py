from PIL import Image
import json
import os
import re

from ..loader.nations import load_nations
from ..bannergen.bannergen import create_banner
from ..bannergen.randombanner import generate_random_banner
from ..util.dirs import (
    input_file,
    defines_file,
    validate_map
)
import re

def clean_name(name: str) -> str:
    if not name:
        return ""

    # Fix UTF-8 mangled section sign
    name = name.replace("Â§", "§")

    # Normalize broken sequences like "§§x" -> "§x"
    name = re.sub(r"§{2,}", "§", name)

    # Remove Minecraft hex color sequences: §x§R§R§G§G§B§B
    name = re.sub(r"§x(?:§[0-9a-fA-F]){6}", "", name)

    # Remove classic formatting codes
    name = re.sub(r"§[0-9A-FK-ORa-fk-or]", "", name)

    # Remove any remaining stray section signs (do NOT remove next char)
    name = name.replace("§", "")

    # Remove hex literals if present (#ffffff)
    name = re.sub(r"#(?:[0-9a-fA-F]{6})", "", name)

    return name.strip()


def clean_banner_patterns(patterns: list) -> list:
    return [pattern.replace("tfmc:", "") for pattern in patterns]


def process_nations(map: str):
    validate_map(map)

    # === Load nations ===
    nations = load_nations(map)

    # === Prepare output paths ===
    output_path = defines_file(map, "nation.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    banner_folder = os.path.join(
        os.path.dirname(output_path),
        "..",
        "output",
        "banner",
        map,
        "nation"
    )
    banner_folder = os.path.abspath(banner_folder)
    os.makedirs(banner_folder, exist_ok=True)

    # Clear old banners
    for file_name in os.listdir(banner_folder):
        file_path = os.path.join(banner_folder, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # === Initialize nations ===
    for nation_id, data in nations.items():
        if not isinstance(data, dict):
            print(f"⚠️ Skipping invalid nation entry: {nation_id}")
            continue

        data.setdefault("subjects", [])

        if "overlord" in data:
            overlord_id = data["overlord"]
            if overlord_id in nations and isinstance(nations[overlord_id], dict):
                nations[overlord_id].setdefault("subjects", []).append(nation_id)

        data["name"] = clean_name(data.get("name", ""))

        if "banner" not in data:
            data["banner"] = generate_random_banner()

        if "banner patterns" in data:
            data["banner patterns"] = clean_banner_patterns(data["banner patterns"])

    # === Recursive size calculation ===
    def calculate_size(nation_id):
        nation = nations[nation_id]
        total_size = len(nation.get("provinces", []))
        subject_size = 0

        for subject_id in nation.get("subjects", []):
            subject_size += calculate_size(subject_id)

        total_size += subject_size
        nation["size"] = total_size
        nation["subject_size"] = subject_size
        return total_size

    for nation_id in nations:
        if "size" not in nations[nation_id]:
            calculate_size(nation_id)

        nation = nations[nation_id]
        rgb = nation["rgb"].split(",")
        banner_id = f"{rgb[0]}_{rgb[1]}_{rgb[2]}"

        create_banner(
            map,
            "nation",
            banner_id,
            nation["banner"]
        )

        nation["banner"] = banner_id

    # === Save final JSON ===
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(nations, f, indent=4)

    print(f"✅ Nations compiled for map '{map}'")
