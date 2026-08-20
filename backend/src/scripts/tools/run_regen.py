"""Operator CLI for map regeneration."""

from __future__ import annotations

import argparse
import os

from ..compile.nation_compiler import process_nations
from ..compile.trade_compiler import process_trade
from ..util.dirs import input_file, validate_map
from ..util.queue import queue_all_for_mode
from ..util.regeneration import _sync_regeneration


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run ProvinceSystem map regeneration locally.",
        epilog=(
            "Examples:\n"
            "  # SF-equivalent: queue every nation, then incremental regen\n"
            "  python -m scripts.tools.run_regen --map main --queue-all nation --type queued\n"
            "\n"
            "  # Full wipe + rebuild nation overlays only (no other modes)\n"
            "  python -m scripts.tools.run_regen --map main --type fullregen:nation\n"
            "\n"
            "  # Full regen (all modes)\n"
            "  python -m scripts.tools.run_regen --map main --type fullregen\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--map", required=True, help="Map id (e.g. main, dev)")
    parser.add_argument(
        "--type",
        default="queued",
        help="Regen type: fullregen, fullregen:<mode>, queued, queued:<mode>, textonly",
    )
    parser.add_argument(
        "--queue-all",
        nargs="*",
        metavar="MODE",
        help=(
            "Queue all regions for the given mode(s) before regen. "
            "With no args, defaults to nation. Compiles nation/trade data first."
        ),
    )
    args = parser.parse_args()

    validate_map(args.map)

    if args.queue_all is not None:
        modes = args.queue_all if args.queue_all else ["nation"]
        process_nations(args.map)
        if os.path.exists(input_file(args.map, "guilds.json")):
            process_trade(args.map)
        for mode in modes:
            queued = queue_all_for_mode(args.map, mode)
            print(f"📋 Queued {len(queued)} region(s) for mode '{mode}'")

    _sync_regeneration(args.map, args.type)


if __name__ == "__main__":
    main()
