from ..loader.provinces import load_provinces
from ..loader.counties import load_counties
from ..loader.duchies import load_duchies
from ..loader.kingdoms import load_kingdoms
from ..loader.nations import load_nations
from ..loader.empires import load_empires
from ..util.dirs import validate_map


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
            duchy_color = county_to_duchy.get(county, (0, 0, 0))
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