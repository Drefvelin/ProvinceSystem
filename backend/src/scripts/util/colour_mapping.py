from ..loader.provinces import load_provinces
from ..loader.counties import load_counties
from ..loader.duchies import load_duchies
from ..loader.kingdoms import load_kingdoms
from ..loader.nations import load_nations
from ..loader.empires import load_empires
from ..loader.guilds import load_guilds
from ..util.dirs import validate_map, input_file
from ..loader.province_metadata import load_province_metadata
import json

SKIP_TERRAINS = {
    "water",
    "sea",
    # "lake",
    # "ocean",
    # "ice",
}


def get_dominant_guild(trade: dict):
    best_guild = None
    best_value = 0.0

    for guild, data in trade.items():
        value = data.get("trade", 0)
        if value > best_value:
            best_value = value
            best_guild = guild

    return best_guild, best_value


def build_color_mapping(map_name: str, mode: str):
    """
    Builds a dictionary mapping province RGB -> target RGB
    based on the selected mode and map.
    """
    validate_map(map_name)

    provinces = load_provinces(map_name)
    counties = load_counties(map_name)
    duchies = load_duchies(map_name)
    kingdoms = load_kingdoms(map_name)
    nations = load_nations(map_name)
    empires = load_empires(map_name)

    province_to_color = {}
    province_meta = load_province_metadata(map_name)

    if mode == "empire":
        kingdom_to_empire = {
            kingdom: tuple(map(int, empires[e]["rgb"].split(",")))
            for e in empires
            for kingdom in empires[e].get("titles", [])
        }

        for kingdom, data in kingdoms.items():
            empire_color = kingdom_to_empire.get(kingdom, (0, 0, 0))
            for duchy in data.get("titles", []):
                if duchy in duchies:
                    for county in duchies[duchy].get("titles", []):
                        if county in counties:
                            for province_id in counties[county].get("provinces", []):
                                for rgb, pid in provinces.items():
                                    if pid == province_id:
                                        province_to_color[rgb] = empire_color

    elif mode == "kingdom":
        duchy_to_kingdom = {
            duchy: tuple(map(int, kingdoms[k]["rgb"].split(",")))
            for k in kingdoms
            for duchy in kingdoms[k].get("titles", [])
        }

        for duchy, data in duchies.items():
            kingdom_color = duchy_to_kingdom.get(duchy, (0, 0, 0))
            for county in data.get("titles", []):
                if county in counties:
                    for province_id in counties[county].get("provinces", []):
                        for rgb, pid in provinces.items():
                            if pid == province_id:
                                province_to_color[rgb] = kingdom_color

    elif mode == "duchy":
        county_to_duchy = {
            county: tuple(map(int, duchies[d]["rgb"].split(",")))
            for d in duchies
            for county in duchies[d].get("titles", [])
        }

        for county, data in counties.items():
            if county not in county_to_duchy:
                continue
            duchy_color = county_to_duchy[county]
            for province_id in data.get("provinces", []):
                for rgb, pid in provinces.items():
                    if pid == province_id:
                        province_to_color[rgb] = duchy_color

    elif mode == "county":
        for county, data in counties.items():
            county_color = tuple(map(int, data["rgb"].split(",")))
            for province_id in data.get("provinces", []):
                for rgb, pid in provinces.items():
                    if pid == province_id:
                        province_to_color[rgb] = county_color

    elif mode == "nation":
        for nation, data in nations.items():
            nation_color = tuple(map(int, data["rgb"].split(",")))
            for province_id in data.get("provinces", []):
                for rgb, pid in provinces.items():
                    if pid == province_id:
                        province_to_color[rgb] = nation_color
    
    elif mode == "guild":
        guilds = load_guilds(map_name)
        province_meta = load_province_metadata(map_name)

        with open(input_file(map_name, "province_data.json"), "r") as f:
            province_data = json.load(f)

        province_by_id = {p["id"]: p for p in province_data}

        for rgb, pid in provinces.items():
            # --- terrain filter ---
            meta = province_meta.get(pid, {})
            terrain = (meta.get("terrain") or "").lower()
            if terrain in SKIP_TERRAINS:
                continue

            pdata = province_by_id.get(pid)
            if not pdata:
                continue

            trade = pdata.get("trade")
            if not trade:
                continue

            dominant, _ = get_dominant_guild(trade)
            if not dominant or dominant not in guilds:
                continue

            province_to_color[rgb] = guilds[dominant]["rgb"]

    return province_to_color


def get_overlord_rgb(nation: str, nations: dict):
    overlord = nations.get(nation, {}).get("overlord")
    if overlord and overlord in nations:
        return tuple(map(int, nations[overlord]["rgb"].split(",")))
    return None


def get_color_overrides(map_name: str, mode: str):
    """
    Maps nation RGB -> immediate overlord RGB.
    Only applies to nation mode.
    """
    validate_map(map_name)

    overrides = {}

    if mode != "nation":
        return overrides

    nations = load_nations(map_name)

    for nation, data in nations.items():
        nation_color = tuple(map(int, data["rgb"].split(",")))
        overlord_rgb = get_overlord_rgb(nation, nations)

        if overlord_rgb:
            overrides[nation_color] = overlord_rgb

    return overrides