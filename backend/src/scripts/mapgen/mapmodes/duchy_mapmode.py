from ..mapgen import create_map
from ..regiongen import generate_regions

create_map("duchy", "duchy_map", True)
generate_regions("duchy", True, True)