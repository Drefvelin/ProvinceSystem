import json
from ..util.dirs import input_file, validate_map


def load_guilds(map_name: str) -> dict:
    validate_map(map_name)

    path = input_file(map_name, "guilds.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {
        g["id"]: {
            "rgb": tuple(map(int, g["rgb"].split(","))),
            "name": g.get("name"),
            "size": g.get("size"),
            "trade_power": g.get("trade_power"),
            "banner": g.get("banner"),  # ✅ ADD THIS
        }
        for g in data
    }
