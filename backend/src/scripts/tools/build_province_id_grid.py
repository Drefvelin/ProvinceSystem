"""Admin CLI: build province_id_grid.bin.gz for SimpleFactions Input."""

from __future__ import annotations

import argparse
import os
import sys

from ..province_id_grid import (
    build_province_id_map,
    decimate_province_id_map,
    lost_province_ids,
    province_id_grid_filename,
    write_province_id_grid_file,
)
from ..util.dirs import defines_file, validate_map


def _report_lost(lost: list[int]) -> bool:
    """Print any provinces decimation erased. True when something was lost."""
    if not lost:
        return False
    shown = ", ".join(str(pid) for pid in lost[:50])
    if len(lost) > 50:
        shown += f", ... (+{len(lost) - 50} more)"
    print(
        f"WARNING: {len(lost)} province(s) vanished at this scale: {shown}",
        file=sys.stderr,
    )
    return True


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
        "--scale",
        type=int,
        default=1,
        help=(
            "Decimate by this integer factor, writing province_id_grid_q{scale}.bin.gz "
            "(default: 1, full resolution). Must divide the map dimensions exactly."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build in memory only; print stats without writing",
    )
    args = parser.parse_args()

    validate_map(args.map)
    if args.scale < 1:
        parser.error(f"--scale must be a positive integer, got {args.scale}")

    width, height, source_ids = build_province_id_map(args.map)
    # Decimate before the dry-run report so an indivisible --scale fails here
    # rather than after a multi-second build the user cannot use anyway.
    try:
        width, height, ids = decimate_province_id_map(
            width, height, source_ids, args.scale
        )
    except ValueError as exc:
        parser.error(str(exc))

    nonzero = int((ids > 0).sum())
    # nonzero_pixels alone cannot show that a whole province was voted out of
    # existence, which is exactly what decimation risks for narrow or tiny ones.
    # Compare the id sets and make the loss impossible to miss.
    lost = lost_province_ids(source_ids, ids)

    if args.dry_run:
        print(
            f"map={args.map} scale={args.scale} width={width} height={height} "
            f"nonzero_pixels={nonzero} "
            f"target={args.output or province_id_grid_filename(args.scale)}"
        )
        _report_lost(lost)
        return

    # `source` is already decimated, so resolve the _q{scale} default path here
    # rather than letting the writer decimate a second time.
    dest = args.output or defines_file(args.map, province_id_grid_filename(args.scale))
    out_path = write_province_id_grid_file(
        args.map, dest=dest, source=(width, height, ids)
    )
    size_bytes = os.path.getsize(out_path)
    print(
        f"Wrote {out_path} ({width}x{height}, {nonzero} province pixels, {size_bytes} bytes gzip)"
    )
    # The artifact is still written: it is optional and the viewer falls back to
    # the full-resolution runs, so a partially lossy grid beats no grid. The
    # non-zero exit is what makes an unattended rebuild (or CI) notice, instead
    # of the old unconditional success message hiding it.
    if _report_lost(lost):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
