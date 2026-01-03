from ...mapgen.prosperitygen import create_prosperity_map
from ...util.dirs import validate_map

MAP = "dev"  # default manual map

validate_map(MAP)

create_prosperity_map(MAP, filename="prosperity_map")