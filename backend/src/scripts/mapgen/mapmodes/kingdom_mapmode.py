from ..mapgen import create_map
from ..regiongen import generate_regions

create_map("kingdom", "kingdom_map", True)
generate_regions("kingdom", True, True)