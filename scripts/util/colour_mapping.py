from ..loader.provinces import load_provinces
from ..loader.counties import load_counties
from ..loader.duchies import load_duchies
from ..loader.kingdoms import load_kingdoms

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

    return province_to_color