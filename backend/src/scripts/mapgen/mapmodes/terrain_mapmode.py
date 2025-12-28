from ...mapgen.terraingen import create_terrain_map
from ...util.dirs import validate_map

MAP = "dev"  # or "dev"

validate_map(MAP)

create_terrain_map(MAP, filename="terrain_map")
