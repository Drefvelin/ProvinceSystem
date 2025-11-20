from ..loader.provinces import load_provinces
from ..loader.counties import load_counties
from ..loader.duchies import load_duchies
from ..loader.kingdoms import load_kingdoms
from ..loader.nations import load_nations
from ..loader.empires import load_empires

def build_color_mapping(mode):
    """
    Builds a dictionary that maps province colors to nation, county, duchy, kingdom, or empire colors
    based on the selected mode.
    """
    # Load base data
    provinces = load_provinces()
    counties = load_counties()
    duchies = load_duchies()
    kingdoms = load_kingdoms()
    nations = load_nations()
    empires = load_empires()  # <-- New!

    province_to_color = {}

    if mode == "empire":
        # Map kingdoms to empire RGB
        kingdom_to_empire = {
            kingdom: tuple(map(int, empires[e]["rgb"].split(",")))
            for e in empires for kingdom in empires[e].get("titles", [])
        }

        for kingdom, data in kingdoms.items():
            empire_color = kingdom_to_empire.get(kingdom, (0, 0, 0))  # Default to black
            for duchy in data.get("titles", []):
                if duchy in duchies:
                    for county in duchies[duchy].get("titles", []):
                        if county in counties:
                            for province_id in counties[county].get("provinces", []):
                                for province_rgb, p_id in provinces.items():
                                    if p_id == province_id:
                                        province_to_color[province_rgb] = empire_color

    elif mode == "kingdom":
        duchy_to_kingdom = {
            duchy: tuple(map(int, kingdoms[k]["rgb"].split(",")))
            for k in kingdoms for duchy in kingdoms[k].get("titles", [])
        }

        for duchy, data in duchies.items():
            kingdom_color = duchy_to_kingdom.get(duchy, (0, 0, 0))
            for county in data.get("titles", []):
                if county in counties:
                    for province_id in counties[county].get("provinces", []):
                        for province_rgb, p_id in provinces.items():
                            if p_id == province_id:
                                province_to_color[province_rgb] = kingdom_color

    elif mode == "duchy":
        county_to_duchy = {
            county: tuple(map(int, duchies[d]["rgb"].split(",")))
            for d in duchies for county in duchies[d].get("titles", [])
        }

        for county, data in counties.items():
            duchy_color = county_to_duchy.get(county, (0, 0, 0))
            for province_id in data.get("provinces", []):
                for province_rgb, p_id in provinces.items():
                    if p_id == province_id:
                        province_to_color[province_rgb] = duchy_color

    elif mode == "county":
        for county, data in counties.items():
            county_color = tuple(map(int, data["rgb"].split(",")))
            for province_id in data.get("provinces", []):
                for province_rgb, p_id in provinces.items():
                    if p_id == province_id:
                        province_to_color[province_rgb] = county_color

    elif mode == "nation":
        for nation, data in nations.items():
            nation_color = tuple(map(int, data["rgb"].split(",")))
            for province_id in data.get("provinces", []):
                for province_rgb, p_id in provinces.items():
                    if p_id == province_id:
                        province_to_color[province_rgb] = nation_color

    return province_to_color


def get_overlord_rgb(nation, nations):
    """
    Retrieves the RGB color of the immediate overlord of a nation.
    """
    overlord_name = nations.get(nation, {}).get("overlord")  # Get overlord's name

    if overlord_name and overlord_name in nations:
        return tuple(map(int, nations[overlord_name]["rgb"].split(",")))  # Get overlord's RGB
    
    return None  # No overlord found


def get_color_overrides(mode):
    """
    Builds a dictionary that maps nation colors to their immediate overlord's color.
    Used to "fix" the nation map after making the canvas.
    """
    overrides = {}

    if mode != "nation":
        return overrides

    # Load nation data
    nations = load_nations()

    for nation, data in nations.items():
        nation_color = tuple(map(int, data["rgb"].split(",")))

        # Check if the nation has an immediate overlord
        overlord_rgb = get_overlord_rgb(nation, nations)
        if overlord_rgb:
            overrides[nation_color] = overlord_rgb  # Map nation color -> immediate overlord color

    return overrides

