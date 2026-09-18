"""Build the Woodworking furniture catalogue for the wiki.

Reads the Woodworking plugin's project configs, resolves each project's ItemsAdder
furniture item to its pack model and textures (recipes are deliberately left out), copies those into `public/wiki`, and
writes `app/wiki/data/generated/woodworkingFurniture.json`.

Usage:
  python scripts/build-woodworking-furniture.py [ItemsAdder contents dir] [Woodworking plugin dir]
"""
import glob
import json
import os
import re
import shutil
import sys

import yaml
from PIL import Image

FRONTEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENTS = sys.argv[1] if len(sys.argv) > 1 else "C:/Users/MSI/Desktop/ItemsAdder-new/contents"
PLUGIN = sys.argv[2] if len(sys.argv) > 2 else "C:/Users/MSI/Desktop/plugins/Woodworking"
MODEL_OUT = os.path.join(FRONTEND, "public", "wiki", "models", "woodworking")
TEXTURE_OUT = os.path.join(FRONTEND, "public", "wiki", "textures", "woodworking")
DATA_OUT = os.path.join(FRONTEND, "app", "wiki", "data", "generated", "woodworkingFurniture.json")


def strip_colour(text):
    return re.sub(r"§.", "", text or "").strip()


def load_yaml(path):
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def index_items():
    """namespace:id -> (pack directory, item config) for every ItemsAdder item."""
    items = {}
    for path in glob.glob(os.path.join(CONTENTS, "**", "*.yml"), recursive=True):
        try:
            data = load_yaml(path)
        except yaml.YAMLError:
            continue
        if not isinstance(data, dict):
            continue
        namespace = (data.get("info") or {}).get("namespace")
        pack = os.path.relpath(path, CONTENTS).split(os.sep)[0]
        for key, value in (data.get("items") or {}).items():
            if isinstance(value, dict):
                items[f"{namespace}:{key}"] = (pack, value)
    return items


def find_asset(pack, kind, namespace, relative, extension):
    """Locate assets/<namespace>/<kind>/<relative> inside a pack, whatever its folder layout."""
    pattern = os.path.join(CONTENTS, pack, "**", namespace, kind, *relative.split("/")) + extension
    matches = glob.glob(pattern, recursive=True)
    return matches[0] if matches else None


def split_ref(ref, default_namespace):
    return ref.split(":", 1) if ":" in ref else (default_namespace, ref)


def main():
    items = index_items()
    categories = load_yaml(os.path.join(PLUGIN, "categories.yml"))

    for directory in (MODEL_OUT, TEXTURE_OUT):
        shutil.rmtree(directory, ignore_errors=True)
        os.makedirs(directory)

    projects = []
    problems = []
    for path in sorted(glob.glob(os.path.join(PLUGIN, "projects", "*.yml"))):
        for key, project in load_yaml(path).items():
            item_id = project["item"].removeprefix("ia.")
            if item_id not in items:
                problems.append(f"{key}: no ItemsAdder item {item_id}")
                continue
            pack, item = items[item_id]
            namespace = item_id.split(":")[0]
            model_path = (item.get("resource") or {}).get("model_path")
            model_ns, model_rel = split_ref(model_path, namespace)
            model_file = find_asset(pack, "models", model_ns, model_rel, ".json")
            if not model_file:
                problems.append(f"{key}: no model {model_path} in {pack}")
                continue
            with open(model_file, encoding="utf-8") as handle:
                model = json.load(handle)

            texture_urls = {}
            animated = {}
            for slot, ref in (model.get("textures") or {}).items():
                texture_ns, texture_rel = split_ref(ref, "minecraft")
                texture_file = find_asset(pack, "textures", texture_ns, texture_rel, ".png")
                if not texture_file:
                    if slot != "particle":
                        problems.append(f"{key}: missing texture {ref}")
                    continue
                name = f"{texture_ns}__{texture_rel.replace('/', '__')}.png"
                shutil.copyfile(texture_file, os.path.join(TEXTURE_OUT, name))
                texture_urls[slot] = f"/wiki/textures/woodworking/{name}"
                if os.path.exists(texture_file + ".mcmeta"):
                    animated[slot] = (texture_file, name)

            # Animated textures are vertical frame strips. The viewer animates a model that has a
            # single texture; otherwise the strip is cut down to its first frame so UVs still fit.
            entry_extra = {}
            slots = {slot for slot in texture_urls if slot != "particle"}
            if animated and len({texture_urls[slot] for slot in slots}) == 1:
                texture_file, name = next(iter(animated.values()))
                shutil.copyfile(texture_file + ".mcmeta", os.path.join(TEXTURE_OUT, name + ".mcmeta"))
                entry_extra = {
                    "textureUrl": f"/wiki/textures/woodworking/{name}",
                    "textureAnimationUrl": f"/wiki/textures/woodworking/{name}.mcmeta",
                }
                texture_urls = {}
            else:
                for texture_file, name in animated.values():
                    with Image.open(texture_file) as strip:
                        with open(texture_file + ".mcmeta", encoding="utf-8") as handle:
                            animation = json.load(handle).get("animation", {})
                        width = animation.get("width", min(strip.size))
                        height = animation.get("height", min(strip.size))
                        strip.crop((0, 0, width, height)).save(os.path.join(TEXTURE_OUT, name))

            shutil.copyfile(model_file, os.path.join(MODEL_OUT, f"{key}.json"))
            projects.append({
                "id": key,
                "name": strip_colour(project.get("name")),
                "category": project["category"],
                "itemId": item_id,
                "modelUrl": f"/wiki/models/woodworking/{key}.json",
                "textureUrls": texture_urls,
                **entry_extra,
            })

    data = {
        "categories": [{"id": key, "name": strip_colour(value["name"])} for key, value in categories.items()],
        "projects": projects,
    }
    with open(DATA_OUT, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")

    print(f"{len(projects)} projects, {len(os.listdir(TEXTURE_OUT))} textures -> {os.path.relpath(DATA_OUT, FRONTEND)}")
    for problem in problems:
        print("PROBLEM", problem)


if __name__ == "__main__":
    main()
