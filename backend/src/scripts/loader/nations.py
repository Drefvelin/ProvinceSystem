import json
from ..util.dirs import input_file, validate_map


def load_nations(map_name: str) -> dict:
    validate_map(map_name)

    file_path = input_file(map_name, "nation.json")

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)
