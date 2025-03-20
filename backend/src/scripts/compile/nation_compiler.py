from ..loader.nations import load_nations
import json
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "defines")

def process_nations():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    nations = load_nations()

    # Initialize "subjects" field
    for nation_id, data in nations.items():
        data.setdefault("subjects", [])  # Ensure "subjects" exists

        # If the nation has an overlord, add it to the overlord's "subjects" list
        if "overlord" in data:
            overlord_id = data["overlord"]
            if overlord_id in nations:
                nations[overlord_id].setdefault("subjects", []).append(nation_id)

    # Recursive function to calculate size (provinces + subjects' provinces)
    def calculate_size(nation_id):
        nation = nations[nation_id]
        total_size = len(nation.get("provinces", []))  # Own provinces

        # Add sizes of all subjects
        for subject_id in nation.get("subjects", []):
            total_size += calculate_size(subject_id)

        # Store computed size in the nation
        nation["size"] = total_size
        return total_size

    # Compute sizes for all nations
    for nation_id in nations:
        if "size" not in nations[nation_id]:  # Avoid redundant calculations
            calculate_size(nation_id)

    # Save modified JSON
    with open(os.path.join(OUTPUT_DIR, "nation.json"), "w", encoding="utf-8") as file:
        json.dump(nations, file, indent=4)


# Run the processing function
process_nations()

print("nations.json has been generated!")