import json
from ..util.dirs import defines_file, validate_map


def load_empires(map_name: str) -> dict:
    validate_map(map_name)

    file_path = defines_file(map_name, "empire.json")

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)
