import os
import json

def load_kingdoms():
    kingdom_file_path = os.path.join(os.path.dirname(__file__), "..", "..", "defines", "kingdom.json")
    with open(kingdom_file_path, "r") as file:
        return json.load(file)