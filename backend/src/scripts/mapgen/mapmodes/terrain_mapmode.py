import argparse

from ...mapgen.terraingen import create_terrain_map
from ...util.dirs import validate_map


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate terrain pick/overlay map PNG")
    parser.add_argument("--map", default="dev", help="Map id (e.g. main, dev)")
    args = parser.parse_args()

    validate_map(args.map)
    create_terrain_map(args.map, filename="terrain_map")


if __name__ == "__main__":
    main()
