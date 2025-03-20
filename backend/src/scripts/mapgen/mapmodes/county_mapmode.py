from ..mapgen import create_map
from ..regiongen import generate_regions

create_map("county", "county_map", True)
generate_regions("county", True, True)


