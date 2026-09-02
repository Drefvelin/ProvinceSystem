"""Read-only integrity check of one map's chronicle:
`python -m src.scripts.chronicle.verify --map main`.

`sha256` is recorded on every capture and, before this, never read back — so a
day whose stored bytes drifted from its manifest was undetectable. Verification
lives here rather than in `resolve_stored_file` on purpose: that runs on every
HTTP request, and hashing a whole day's payload per request is not affordable.
This walks the index instead, so the cost is paid once, deliberately.

Exits non-zero when anything is wrong. Nothing here writes.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import sys

from ..util.dirs import validate_map
from .store import (
    get_snapshot,
    list_days,
    resolve_stored_file,
    stored_file_path,
)


def _sha256_of_gz(path: str) -> str | None:
    """sha256 of the *uncompressed* bytes — that is what the manifest records."""
    digest = hashlib.sha256()
    try:
        with gzip.open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                digest.update(chunk)
    except (OSError, EOFError, gzip.BadGzipFile):
        return None
    return digest.hexdigest()


def verify_map(map_name: str) -> list[str]:
    """Return one human-readable line per problem found. Empty means healthy."""
    validate_map(map_name)
    problems: list[str] = []

    for day in list_days(map_name):
        snapshot = get_snapshot(map_name, day)
        if snapshot is None:
            # list_days and get_snapshot read the same table; a gap here means
            # the index changed underneath us or the manifest is unreadable.
            problems.append(f"{day}: index row disappeared while verifying")
            continue

        manifest = snapshot["manifest"] or {}
        if not manifest:
            problems.append(f"{day}: manifest is empty or unparsable JSON")
            continue

        for name in manifest.get("missing") or []:
            problems.append(f"{day}/{name}: source was absent at capture time")
        for name in manifest.get("invalid") or []:
            problems.append(f"{day}/{name}: source was unparsable at capture time")

        files = manifest.get("files") or {}
        for name, entry in sorted(files.items()):
            if not isinstance(entry, dict):
                problems.append(f"{day}/{name}: manifest entry is not an object")
                continue

            same_as = entry.get("same_as")
            path = resolve_stored_file(map_name, day, name)
            if path is None:
                if same_as:
                    problems.append(
                        f"{day}/{name}: dangling same_as -> {same_as} "
                        "(target day has no resolvable bytes)"
                    )
                else:
                    expected = stored_file_path(map_name, day, name)
                    problems.append(f"{day}/{name}: stored file missing at {expected}")
                continue

            expected_sha = entry.get("sha256")
            if not isinstance(expected_sha, str) or not expected_sha:
                problems.append(f"{day}/{name}: manifest records no sha256")
                continue

            actual = _sha256_of_gz(path)
            if actual is None:
                problems.append(f"{day}/{name}: {path} is not readable gzip")
            elif actual != expected_sha:
                where = f" (via same_as -> {same_as})" if same_as else ""
                problems.append(
                    f"{day}/{name}: sha256 mismatch{where} — manifest "
                    f"{expected_sha[:12]}…, on disk {actual[:12]}… at {path}"
                )

    return problems


def main(argv: list[str] | None = None) -> int:
    # cp1252 consoles cannot encode the arrow/ellipsis in the problem lines, and
    # this is the tool an operator reaches for when they already suspect the
    # history is wrong. Same idiom as scripts/tools/build_province_id_grid.py.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Re-hash every stored chronicle file and report drift.",
    )
    parser.add_argument("--map", required=True, help="Map id, e.g. main")
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Print only problems, not the healthy summary.",
    )
    args = parser.parse_args(argv)

    try:
        problems = verify_map(args.map)
    except ValueError as exc:
        parser.error(str(exc))
        return 2

    days = len(list_days(args.map))
    if problems:
        for line in problems:
            print(line, file=sys.stderr)
        print(
            f"{len(problems)} problem(s) across {days} day(s) for map '{args.map}'.",
            file=sys.stderr,
        )
        return 1

    if not args.quiet:
        print(f"OK: {days} day(s) verified for map '{args.map}'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
