import argparse

from ...mapgen.fertilitygen import create_fertility_map
from ...util.dirs import validate_map


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate fertility pick/overlay map PNG")
    parser.add_argument("--map", default="dev", help="Map id (e.g. main, dev)")
    args = parser.parse_args()

    validate_map(args.map)
    create_fertility_map(args.map, filename="fertility_map")


if __name__ == "__main__":
    main()
