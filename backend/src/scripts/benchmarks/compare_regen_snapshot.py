"""Compare two regen benchmark snapshots by manifest (and optional per-pixel PNG diff)."""

from __future__ import annotations

import argparse
import json
import os

from PIL import Image

from ..util.dirs import validate_map
from .paths import manifest_path, snapshot_dir


def _load_manifest(label: str) -> dict:
    path = manifest_path(label)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Manifest not found: {path}")
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _compare_pixels(map_name: str, rel_path: str, label_a: str, label_b: str) -> dict:
    path_a = os.path.join(snapshot_dir(label_a), rel_path)
    path_b = os.path.join(snapshot_dir(label_b), rel_path)

    if not os.path.isfile(path_a) or not os.path.isfile(path_b):
        return {
            "rel_path": rel_path,
            "skipped": True,
            "reason": "snapshot PNG missing",
        }

    image_a = Image.open(path_a).convert("RGBA")
    image_b = Image.open(path_b).convert("RGBA")

    if image_a.size != image_b.size:
        return {
            "rel_path": rel_path,
            "skipped": True,
            "reason": f"size mismatch {image_a.size} vs {image_b.size}",
        }

    pixels_a = image_a.load()
    pixels_b = image_b.load()
    width, height = image_a.size
    mismatch_count = 0
    max_delta = 0

    for y in range(height):
        for x in range(width):
            channel_a = pixels_a[x, y]
            channel_b = pixels_b[x, y]
            if channel_a != channel_b:
                mismatch_count += 1
                for idx in range(4):
                    max_delta = max(max_delta, abs(channel_a[idx] - channel_b[idx]))

    return {
        "rel_path": rel_path,
        "skipped": False,
        "mismatch_pixels": mismatch_count,
        "max_channel_delta": max_delta,
    }


def compare(
    map_name: str,
    label_a: str,
    label_b: str,
    *,
    pixels: bool = False,
) -> dict:
    validate_map(map_name)

    manifest_a = _load_manifest(label_a)
    manifest_b = _load_manifest(label_b)

    if manifest_a.get("map") != map_name or manifest_b.get("map") != map_name:
        raise ValueError(f"Both manifests must be for map '{map_name}'")

    files_a: dict = manifest_a.get("files", {})
    files_b: dict = manifest_b.get("files", {})

    paths_a = set(files_a)
    paths_b = set(files_b)

    added = sorted(paths_b - paths_a)
    removed = sorted(paths_a - paths_b)
    common = sorted(paths_a & paths_b)

    size_changed = []
    sha_mismatches = []

    for rel_path in common:
        meta_a = files_a[rel_path]
        meta_b = files_b[rel_path]
        if meta_a.get("bytes") != meta_b.get("bytes"):
            size_changed.append(rel_path)
        if meta_a.get("sha256") != meta_b.get("sha256"):
            sha_mismatches.append(rel_path)

    result = {
        "map": map_name,
        "a": label_a,
        "b": label_b,
        "identical": not added and not removed and not size_changed and not sha_mismatches,
        "added": added,
        "removed": removed,
        "size_changed": size_changed,
        "sha256_mismatches": sha_mismatches,
        "file_count_a": len(files_a),
        "file_count_b": len(files_b),
    }

    if pixels and sha_mismatches:
        pixel_reports = []
        for rel_path in sha_mismatches:
            if rel_path.lower().endswith(".png"):
                pixel_reports.append(
                    _compare_pixels(map_name, rel_path, label_a, label_b)
                )
        result["pixel_reports"] = pixel_reports

    return result


def _print_report(result: dict) -> None:
    print(f"Compare {result['a']} vs {result['b']} (map={result['map']})")
    print(f"  files: {result['file_count_a']} vs {result['file_count_b']}")

    if result["identical"]:
        print("  result: IDENTICAL")
        return

    print("  result: DIFFER")

    if result["added"]:
        print(f"  added ({len(result['added'])}):")
        for path in result["added"][:20]:
            print(f"    + {path}")
        if len(result["added"]) > 20:
            print(f"    ... and {len(result['added']) - 20} more")

    if result["removed"]:
        print(f"  removed ({len(result['removed'])}):")
        for path in result["removed"][:20]:
            print(f"    - {path}")
        if len(result["removed"]) > 20:
            print(f"    ... and {len(result['removed']) - 20} more")

    if result["size_changed"]:
        print(f"  size changed ({len(result['size_changed'])}):")
        for path in result["size_changed"][:20]:
            print(f"    ~ {path}")

    if result["sha256_mismatches"]:
        print(f"  sha256 mismatches ({len(result['sha256_mismatches'])}):")
        for path in result["sha256_mismatches"][:20]:
            print(f"    ! {path}")

    for report in result.get("pixel_reports", []):
        if report.get("skipped"):
            print(f"  pixels {report['rel_path']}: skipped ({report['reason']})")
        else:
            print(
                f"  pixels {report['rel_path']}: "
                f"{report['mismatch_pixels']} mismatches, "
                f"max channel delta {report['max_channel_delta']}"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare regen benchmark snapshots")
    parser.add_argument("--map", required=True, help="Map name (e.g. main)")
    parser.add_argument("--a", required=True, help="Baseline label")
    parser.add_argument("--b", required=True, help="Candidate label")
    parser.add_argument(
        "--pixels",
        action="store_true",
        help="Per-pixel PNG compare for sha256 mismatches (requires snapshot dirs)",
    )
    args = parser.parse_args()

    result = compare(args.map, args.a, args.b, pixels=args.pixels)
    _print_report(result)


if __name__ == "__main__":
    main()
