"""Run fullregen, record timings, and snapshot output.

POST-OPTIMIZATION ONLY — do not use this to capture v0-baseline.
Use snapshot_regen.py when output/{map}/ is already fresh.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone

from ..util.dirs import validate_map
from ..util.regeneration import _sync_regeneration
from .paths import TIMINGS_DIR
from .snapshot_regen import snapshot


def _git_short_sha() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=os.path.abspath(os.path.join(TIMINGS_DIR, "..", "..", "..")),
        )
        return result.stdout.strip() or None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_benchmark(map_name: str, label: str, *, regen_type: str = "fullregen") -> str:
    validate_map(map_name)

    timings, elapsed = _sync_regeneration(map_name, regen_type)
    timing_data = timings.to_dict(map_name, regen_type, elapsed)
    timing_data["label"] = label
    timing_data["captured_at"] = datetime.now(timezone.utc).isoformat()
    timing_data["git_commit"] = _git_short_sha()
    timing_data["source"] = "run_benchmark_regen"

    os.makedirs(TIMINGS_DIR, exist_ok=True)
    timing_path = os.path.join(TIMINGS_DIR, f"{label}.json")
    with open(timing_path, "w", encoding="utf-8") as handle:
        json.dump(timing_data, handle, indent=2)
        handle.write("\n")

    print(f"Wrote timings: {timing_path}")

    snapshot(
        map_name,
        label,
        copy_files=True,
        source="run_benchmark_regen",
        regen_type=regen_type,
    )

    return timing_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run fullregen and capture benchmark timings + snapshot",
        epilog=(
            "POST-OPTIMIZATION ONLY. For baseline capture from existing output, "
            "use: python -m scripts.benchmarks.snapshot_regen"
        ),
    )
    parser.add_argument("--map", required=True, help="Map name (e.g. main)")
    parser.add_argument("--label", required=True, help="Benchmark label (e.g. v1-map-paint)")
    parser.add_argument(
        "--regen-type",
        default="fullregen",
        help="Regeneration type passed to _sync_regeneration (default: fullregen)",
    )
    args = parser.parse_args()

    run_benchmark(args.map, args.label, regen_type=args.regen_type)


if __name__ == "__main__":
    main()
