"""Admin CLI: build province_id_grid.bin.gz for SimpleFactions Input."""

from __future__ import annotations

import argparse
import os
import sys

from ..province_id_grid import build_province_id_map, write_province_id_grid_file
from ..util.dirs import validate_map


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Build province_id_grid.bin.gz from provinces.png (admin, run when map changes)"
    )
    parser.add_argument("--map", required=True, help="Map id (e.g. main, dev)")
    parser.add_argument(
        "--output",
        default=None,
        help="Override output path (default: defines/{map}/province_id_grid.bin.gz)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build in memory only; print stats without writing",
    )
    args = parser.parse_args()

    validate_map(args.map)

    width, height, ids = build_province_id_map(args.map)
    nonzero = int((ids > 0).sum())

    if args.dry_run:
        print(f"map={args.map} width={width} height={height} nonzero_pixels={nonzero}")
        return

    out_path = write_province_id_grid_file(args.map, dest=args.output)
    size_bytes = os.path.getsize(out_path)
    print(
        f"Wrote {out_path} ({width}x{height}, {nonzero} province pixels, {size_bytes} bytes gzip)"
    )


if __name__ == "__main__":
    main()
