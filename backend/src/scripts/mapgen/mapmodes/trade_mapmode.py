from ...mapgen.mapgen import create_map
from ...mapgen.regiongen import generate_regions
from ...util.dirs import validate_map

MAP = "dev"  # default manual map

validate_map(MAP)

# Base trade (guild-dominance) map for canvas use
create_map(MAP, "trade", "trade_map", False)

# Trade regions for hover / interaction
# Toggle borders to test visuals
generate_regions(MAP, "trade", borders=False)