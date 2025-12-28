from ...mapgen.fertilitygen import create_fertility_map
from ...util.dirs import validate_map

MAP = "dev"  # default manual map

validate_map(MAP)

create_fertility_map(MAP, filename="fertility_map")