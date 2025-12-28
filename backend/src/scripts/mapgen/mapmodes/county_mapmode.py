from ...mapgen.mapgen import create_map
from ..regiongen import generate_regions


MAP = "dev"  # default manual map

create_map(MAP, "county", "county_map")
generate_regions(MAP, "county", borders=True)


