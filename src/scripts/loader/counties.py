import os
import json

def load_counties():
    county_file_path = os.path.join(os.path.dirname(__file__), "..", "..", "defines", "counties.json")
    with open(county_file_path, "r") as file:
        return json.load(file)