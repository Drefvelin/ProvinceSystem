"""Generate spoof province_data.json from guilds.json and provinces.txt metadata."""

from __future__ import annotations

import argparse
import json
import random
import sys

from ..loader.province_metadata import load_province_metadata
from ..util.dirs import input_file, validate_map

SKIP_TERRAINS = {"sea", "water"}


def default_seed(map_name: str) -> int:
    return sum(ord(c) for c in map_name) % (2**31)


def generate_province_data(map_name: str, seed: int) -> list[dict]:
    validate_map(map_name)

    guilds_path = input_file(map_name, "guilds.json")
    with open(guilds_path, encoding="utf-8") as f:
        guilds = json.load(f)

    guild_ids = [g["id"] for g in guilds]
    if not guild_ids:
        raise ValueError(f"No guilds found in {guilds_path}")

    metadata = load_province_metadata(map_name)
    rng = random.Random(seed)
    out: list[dict] = []

    for pid in sorted(metadata.keys()):
        meta = metadata[pid]
        terrain = (meta.get("terrain") or "").lower()

        entry: dict = {"id": pid}

        if terrain in SKIP_TERRAINS:
            entry["prosperity"] = 0
            out.append(entry)
            continue

        entry["prosperity"] = round(rng.uniform(10, 100), 2)

        weights = {gid: rng.random() + 0.01 for gid in guild_ids}
        entry["trade"] = {
            gid: {
                "trade": round(w, 2),
                "production": round(w * 0.3, 2),
            }
            for gid, w in weights.items()
        }
        out.append(entry)

    return out


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Generate spoof province_data.json for trade/prosperity maps"
    )
    parser.add_argument("--map", required=True, help="Map id (e.g. main, dev)")
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed (default: derived from map name)",
    )
    args = parser.parse_args()

    seed = args.seed if args.seed is not None else default_seed(args.map)
    data = generate_province_data(args.map, seed)

    out_path = input_file(args.map, "province_data.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    land = sum(1 for p in data if p.get("trade"))
    print(f"Wrote {len(data)} provinces ({land} with trade) to {out_path} (seed={seed})")


if __name__ == "__main__":
    main()
