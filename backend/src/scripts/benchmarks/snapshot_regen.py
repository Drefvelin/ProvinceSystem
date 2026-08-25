"""Snapshot map regeneration output into a benchmark manifest (+ optional PNG copy)."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone

from ..util.dirs import OUTPUT_DIR, validate_map
from .paths import MANIFESTS_DIR, output_subdirs, snapshot_dir


def _git_short_sha() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=os.path.abspath(os.path.join(OUTPUT_DIR, "..", "..", "..")),
        )
        return result.stdout.strip() or None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _hash_file(path: str) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with open(path, "rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def collect_files(map_name: str) -> dict[str, dict[str, int | str]]:
    output_root = os.path.join(OUTPUT_DIR, map_name)
    files: dict[str, dict[str, int | str]] = {}

    for subdir in output_subdirs(map_name):
        if not os.path.isdir(subdir):
            continue
        for root, _, filenames in os.walk(subdir):
            for filename in filenames:
                abs_path = os.path.join(root, filename)
                rel_path = os.path.relpath(abs_path, output_root).replace("\\", "/")
                sha256, size = _hash_file(abs_path)
                files[rel_path] = {"sha256": sha256, "bytes": size}

    return files


def snapshot(
    map_name: str,
    label: str,
    *,
    copy_files: bool = True,
    source: str = "snapshot_only",
    notes: str | None = None,
    regen_type: str = "fullregen",
) -> str:
    validate_map(map_name)

    files = collect_files(map_name)
    if not files:
        raise FileNotFoundError(
            f"No benchmark files found under output/{map_name}/maps or regions/"
        )

    manifest = {
        "label": label,
        "map": map_name,
        "regen_type": regen_type,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_short_sha(),
        "source": source,
        "notes": notes,
        "file_count": len(files),
        "files": files,
    }

    os.makedirs(MANIFESTS_DIR, exist_ok=True)
    manifest_path = os.path.join(MANIFESTS_DIR, f"{label}.json")
    with open(manifest_path, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
        handle.write("\n")

    if copy_files:
        dest_root = snapshot_dir(label)
        if os.path.exists(dest_root):
            shutil.rmtree(dest_root)
        os.makedirs(dest_root, exist_ok=True)

        output_root = os.path.join(OUTPUT_DIR, map_name)
        for rel_path in sorted(files):
            src = os.path.join(output_root, rel_path)
            dst = os.path.join(dest_root, rel_path)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)

    print(f"Wrote manifest: {manifest_path} ({len(files)} files)")
    if copy_files:
        print(f"Copied snapshots: {snapshot_dir(label)}")

    return manifest_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Snapshot regen output for benchmarks")
    parser.add_argument("--map", required=True, help="Map name (e.g. main)")
    parser.add_argument("--label", required=True, help="Benchmark label (e.g. v0-baseline)")
    parser.add_argument(
        "--no-copy",
        action="store_true",
        help="Write manifest only; do not copy PNGs to snapshots/",
    )
    parser.add_argument("--notes", default=None, help="Optional manifest notes")
    args = parser.parse_args()

    snapshot(
        args.map,
        args.label,
        copy_files=not args.no_copy,
        notes=args.notes,
    )


if __name__ == "__main__":
    main()
