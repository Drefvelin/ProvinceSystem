from ..util.dirs import defines_file, validate_map
import os

def load_provinces(map_name: str) -> dict[tuple[int, int, int], int]:
    """
    Loads province RGB -> province_id mappings for a given map.
    """
    validate_map(map_name)

    province_file_path = defines_file(map_name, "provinces.txt")
    provinces: dict[tuple[int, int, int], int] = {}

    if not os.path.exists(province_file_path):
        raise FileNotFoundError(
            f"provinces.txt not found for map '{map_name}'"
        )

    with open(province_file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("##"):
                continue

            try:
                province_id, rgb_values = line.split(" = ")
                rgb = tuple(map(int, rgb_values.split(",")))
                provinces[rgb] = int(province_id)
            except ValueError:
                raise ValueError(
                    f"Invalid line in {province_file_path}: {line}"
                )

    return provinces