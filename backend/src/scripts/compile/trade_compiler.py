import json
import os

from ..loader.guilds import load_guilds
from ..util.dirs import (
    input_file,
    defines_file,
    validate_map
)
from ..bannergen.bannergen import create_banner
from ..bannergen.randombanner import generate_random_banner
import re

def clean_banner_patterns(patterns: list[str]) -> list[str]:
    return [p.replace("tfmc:", "") for p in patterns]

def clean_name(name: str) -> str:
    if not name:
        return ""

    # Handle UTF-8 mangled section sign
    name = name.replace("Â§", "§")

    # Remove classic MC formatting (§a, §x, etc)
    name = re.sub(r"§.", "", name)

    # Remove hex color leftovers (#ffffff)
    name = re.sub(r"#(?:[0-9a-fA-F]{6})", "", name)

    return name.strip()


def get_dominant_guild(trade: dict):
    best_guild = None
    best_value = 0.0

    for guild, data in trade.items():
        value = data.get("trade", 0)
        if value > best_value:
            best_value = value
            best_guild = guild

    return best_guild


def process_trade(map_name: str):
    validate_map(map_name)

    # === Load data ===
    guilds = load_guilds(map_name)

    with open(input_file(map_name, "province_data.json"), "r") as f:
        province_data = json.load(f)

    # === Prepare output paths ===
    output_path = defines_file(map_name, "trade.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    banner_folder = os.path.abspath(
        os.path.join(
            os.path.dirname(output_path),
            "..",
            "output",
            "banner",
            map_name,
            "trade"
        )
    )
    os.makedirs(banner_folder, exist_ok=True)

    # Clear old banners
    for file_name in os.listdir(banner_folder):
        file_path = os.path.join(banner_folder, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # === Initialize trade regions ===
    trade_regions = {}

    for guild_id, guild in guilds.items():
        banner_pattern = guild.get("banner") or generate_random_banner()

        rgb = guild["rgb"]  # tuple[int, int, int]
        banner_id = f"{rgb[0]}_{rgb[1]}_{rgb[2]}"

        raw_patterns = guild.get("banner")
        if isinstance(raw_patterns, list) and raw_patterns:
            banner_pattern = clean_banner_patterns(raw_patterns)
        else:
            banner_pattern = generate_random_banner()

        trade_regions[guild_id] = {
            "name": clean_name(guild.get("name", guild_id)),
            "rgb": f"{rgb[0]},{rgb[1]},{rgb[2]}",
            "tier": "trade",
            "size": 0,
            "subjects": [],
            "overlord": None,
            "banner": banner_id,
            "_banner_pattern": banner_pattern,  # consumed by create_banner
        }


    # === Count dominant provinces ===
    for pdata in province_data:
        trade = pdata.get("trade")
        if not trade:
            continue

        dominant = get_dominant_guild(trade)
        if dominant and dominant in trade_regions:
            trade_regions[dominant]["size"] += 1

    # === Generate banners & prune unused guilds ===
    for guild_id in list(trade_regions.keys()):
        data = trade_regions[guild_id]

        if data["size"] <= 0:
            del trade_regions[guild_id]
            continue

        create_banner(
            map_name,
            "trade",
            data["banner"],
            data["_banner_pattern"]
        )

        del data["_banner_pattern"]

    # === Save final JSON ===
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(trade_regions, f, indent=4)

    print(f"💱 Trade compiled for map '{map_name}'")

process_trade("dev")
