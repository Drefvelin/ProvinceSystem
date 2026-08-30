import argparse
import sys

from ...mapgen.infestationgen import create_infestation_map
from ...util.dirs import validate_map


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Generate infestation overlay map PNG")
    parser.add_argument("--map", default="dev", help="Map id (e.g. main, dev)")
    args = parser.parse_args()

    validate_map(args.map)
    create_infestation_map(args.map, filename="infestation_map")


if __name__ == "__main__":
    main()
