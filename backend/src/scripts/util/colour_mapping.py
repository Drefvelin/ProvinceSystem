from ..loader.provinces import load_provinces
from ..loader.counties import load_counties
from ..loader.duchies import load_duchies
from ..loader.kingdoms import load_kingdoms
from ..loader.nations import load_nations

def build_color_mapping(mode):
    """
    Builds a dictionary that maps province colors to county, duchy, or kingdom colors
    based on the selected mode.
    """
    # Load the provinces from the provinces.txt file
    provinces = load_provinces()

    # Load the counties, duchies, and kingdoms
    counties = load_counties()
    duchies = load_duchies()
    kingdoms = load_kingdoms()
    nations = load_nations()

    province_to_color = {}

    if mode == "kingdom":
        duchy_to_kingdom = {duchy: tuple(map(int, kingdoms[k]["rgb"].split(","))) for k in kingdoms for duchy in kingdoms[k]["duchies"]}

        for duchy, data in duchies.items():
            kingdom_color = duchy_to_kingdom.get(duchy, (0, 0, 0))  # Default to black if not found
            for county in data["counties"]:
                if county in counties:
                    for province_id in counties[county]["provinces"]:
                        for province_rgb, p_id in provinces.items():
                            if p_id == province_id:
                                province_to_color[province_rgb] = kingdom_color

    elif mode == "duchy":
        county_to_duchy = {county: tuple(map(int, duchies[d]["rgb"].split(","))) for d in duchies for county in duchies[d]["counties"]}

        for county, data in counties.items():
            duchy_color = county_to_duchy.get(county, (0, 0, 0))  # Default to black
            for province_id in data["provinces"]:
                for province_rgb, p_id in provinces.items():
                    if p_id == province_id:
                        province_to_color[province_rgb] = duchy_color

    elif mode == "county":
        for county, data in counties.items():
            county_color = tuple(map(int, data["rgb"].split(",")))
            for province_id in data["provinces"]:
                for province_rgb, p_id in provinces.items():
                    if p_id == province_id:
                        province_to_color[province_rgb] = county_color
    elif mode == "nation":
        for nation, data in nations.items():
            nation_color = tuple(map(int, data["rgb"].split(",")))
            for province_id in data["provinces"]:
                for province_rgb, p_id in provinces.items():
                    if p_id == province_id:
                        province_to_color[province_rgb] = nation_color

    return province_to_color

def get_overlord_rgb(nation, nations):
    """
    Recursively finds the topmost overlord's RGB color.
    If a nation has no overlord, returns its own color.
    """
    if "overlord" in nations[nation] and nations[nation]["overlord"] in nations:
        return get_overlord_rgb(nations[nation]["overlord"], nations)  # Recursively go up the chain
    return tuple(map(int, nations[nation]["rgb"].split(",")))  # Return top overlord's color

def get_color_overrides(mode):
    """
    Builds a dictionary that maps nation colors to their overlord's color.
    Used to "fix" the nation map after making the canvas.
    """
    overrides = {}

    if mode != "nation":
        return overrides

    # Load nation data
    nations = load_nations()

    for nation, data in nations.items():
        nation_color = tuple(map(int, data["rgb"].split(",")))

        # Check if the nation has an overlord
        if "overlord" in data and data["overlord"] in nations:
            overlord_rgb = get_overlord_rgb(nation, nations)
            overrides[nation_color] = overlord_rgb  # Nation color -> Overlord color mapping

    return overrides
