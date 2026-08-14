"""CLI: build province_neighbors.json and province_centroids.json for a map."""

import sys

from .province_geometry import write_province_geometry


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print("Usage: python -m scripts.map_tools.build_province_geometry <map>")
        return 1

    map_name = args[0]
    write_province_geometry(map_name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
