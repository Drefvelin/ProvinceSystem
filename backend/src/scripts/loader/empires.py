import os
import json

def load_empires():
    empire_file_path = os.path.join(os.path.dirname(__file__), "..", "..", "defines", "empire.json")
    with open(empire_file_path, "r") as file:
        return json.load(file)