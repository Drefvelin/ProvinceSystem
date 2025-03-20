import os
import json

def load_nations():
    file_path = os.path.join(os.path.dirname(__file__), "..", "..", "input", "nation.json")
    with open(file_path, "r") as file:
        return json.load(file)