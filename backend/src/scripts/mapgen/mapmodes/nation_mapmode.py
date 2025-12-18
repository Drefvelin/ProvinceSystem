from ..mapgen import create_map
from ..regiongen import generate_regions

MAP = "main"  # default manual map

#create_map(MAP, "nation", "nation_map", True)
generate_regions(MAP, "nation", True, True)


