import os
import json

def load_duchies():
    duchy_file_path = os.path.join(os.path.dirname(__file__), "..", "..", "defines", "duchy.json")
    with open(duchy_file_path, "r") as file:
        return json.load(file)