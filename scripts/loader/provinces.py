import os

def load_provinces():
    province_file_path = os.path.join(os.path.dirname(__file__), "..", "..", "defines", "provinces.txt")
    provinces = {}

    with open(province_file_path, "r") as file:
        for line in file:
            if line.startswith("##") or not line.strip():
                continue
            province_id, rgb_values = line.split(" = ")
            rgb_values = tuple(map(int, rgb_values.split(",")))
            provinces[rgb_values] = int(province_id.strip())
    return provinces