from ..mapgen import create_map
from ..regiongen import generate_regions

MAP = "main"  # default manual map

create_map(MAP, "kingdom", "kingdom_map")
generate_regions(MAP, "kingdom", True)