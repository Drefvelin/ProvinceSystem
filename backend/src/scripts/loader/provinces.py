from ..util.dirs import defines_file, validate_map
import os

def load_provinces(map_name: str) -> dict[tuple[int, int, int], int]:
    """
    Loads province RGB -> province_id mappings for a given map.
    Backward-compatible with old and new provinces.txt formats.
    """
    validate_map(map_name)

    province_file_path = defines_file(map_name, "provinces.txt")
    provinces: dict[tuple[int, int, int], int] = {}

    if not os.path.exists(province_file_path):
        raise FileNotFoundError(
            f"provinces.txt not found for map '{map_name}'"
        )

    with open(province_file_path, "r", encoding="utf-8") as file:
        for line_num, line in enumerate(file, start=1):
            line = line.strip()

            if not line or line.startswith("##"):
                continue

            try:
                # Split province id from rest
                province_id_str, rest = line.split("=", 1)
                province_id = int(province_id_str.strip())

                # RGB is always the first field (before any ;)
                rgb_part = rest.split(";", 1)[0].strip()
                rgb = tuple(map(int, rgb_part.split(",")))

                if len(rgb) != 3:
                    raise ValueError("RGB must have exactly 3 values")

                provinces[rgb] = province_id

            except Exception as e:
                raise ValueError(
                    f"Invalid line in {province_file_path} "
                    f"(line {line_num}): {line}"
                ) from e

    return provinces