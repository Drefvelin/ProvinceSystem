"""Capture one day's map state into the chronicle store."""

from __future__ import annotations

import gzip
import hashlib
import json
import logging
import os
import tempfile
import threading
import time

from ..util.dirs import defines_file, input_file, validate_map
from .store import (
    CHRONICLE_FILES,
    chronicle_day_dir,
    days_referencing,
    geometry_version,
    get_snapshot,
    is_valid_day,
    previous_snapshot,
    realm_for_map,
    stored_file_path,
    today_utc,
    upsert_snapshot,
)

logger = logging.getLogger(__name__)

# `nation`/`trade`/`zoc_overlays` live in defines/ because they are the
# *resolved* artifacts the map viewer reads; the rest are raw SF uploads
# that data_routes writes into input/.
_DEFINES_SOURCES = frozenset({"nation", "trade", "zoc_overlays"})


class ChronicleForwardReferenceError(RuntimeError):
    """Raised when re-capturing a day that later days dedup against."""


def _source_path(map_name: str, name: str) -> str:
    filename = f"{name}.json"
    if name in _DEFINES_SOURCES:
        return defines_file(map_name, filename)
    return input_file(map_name, filename)


# Captures are scheduled on *every* upload and run synchronously in the
# threadpool, so several full captures for the same (map, day) can be in flight
# at once. A `threading.Lock` is the right primitive here rather than an
# O_EXCL lockfile: everything that captures lives in this one process (the
# asyncio.Lock in scripts/util/task_lock.py is unusable because this code is
# not async), and a lockfile would need stale-owner detection to stop a killed
# process from wedging captures forever. One entry per (map, day) that this
# process actually captures — bounded by days of uptime, so never pruned.
_DAY_LOCKS_GUARD = threading.Lock()
_DAY_LOCKS: dict[tuple[str, str], threading.Lock] = {}


def _day_lock(map_name: str, day: str) -> threading.Lock:
    key = (map_name, day)
    with _DAY_LOCKS_GUARD:
        lock = _DAY_LOCKS.get(key)
        if lock is None:
            lock = threading.Lock()
            _DAY_LOCKS[key] = lock
        return lock


def _fsync_dir(directory: str) -> None:
    """Persist the rename itself. No-op where the platform forbids it."""
    if not hasattr(os, "O_DIRECTORY"):
        # Windows cannot open a directory as a file descriptor.
        return
    try:
        fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


def _write_atomic(path: str, data: bytes) -> None:
    """Write via a unique temp sibling so a crash never leaves a truncated file.

    The temp name must be unique, not a fixed `<path>.tmp`: a fixed sibling is
    atomic against a crash but not against a second writer, and two concurrent
    captures would either interleave into a corrupt file (POSIX) or raise
    PermissionError on the loser (Windows).
    """
    directory = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".chronicle-", suffix=".part")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            # os.replace orders the rename, not the data: without this a power
            # loss can leave a zero-length file where the manifest promises
            # content, and this is the only copy of the day.
            os.fsync(fh.fileno())
        os.replace(tmp, path)
        tmp = None
    finally:
        if tmp is not None:
            try:
                os.unlink(tmp)
            except OSError:
                pass
    _fsync_dir(directory)


def _is_incomplete(manifest: dict) -> bool:
    """True when a capture did not record every source it found or expected."""
    return bool(manifest.get("missing")) or bool(manifest.get("invalid"))


def capture_snapshot(
    map_name: str,
    day: str | None = None,
    force: bool = False,
) -> dict | None:
    """Snapshot today's (or `day`'s) sources. Returns None if already captured."""
    validate_map(map_name)
    day = day or today_utc()
    if not is_valid_day(day):
        raise ValueError("Invalid chronicle day")

    with _day_lock(map_name, day):
        return _capture_locked(map_name, day, force)


def _capture_locked(map_name: str, day: str, force: bool) -> dict | None:
    """Body of `capture_snapshot`; caller must hold this day's lock."""
    existing = get_snapshot(map_name, day)
    if existing is not None and not force:
        return None

    if force:
        # Refuse rather than auto-materialising the forward references: the
        # legitimate use of `force` is fixing *today*, which by definition has
        # no later days pointing at it.
        blocking = days_referencing(map_name, day)
        if blocking:
            raise ChronicleForwardReferenceError(
                f"Refusing to re-capture {map_name} {day}: "
                f"{', '.join(blocking)} dedup against it and would silently "
                "change content. Capture a fresh day instead, or wipe the "
                "later days first (python -m src.scripts.chronicle.wipe)."
            )

    # Dedup baseline: the newest day already captured, strictly before the one
    # we are about to (re)write so `force` cannot point a file at itself.
    baseline = previous_snapshot(map_name, day)
    previous_day = baseline["day"] if baseline else None
    previous_files = (baseline["manifest"].get("files") or {}) if baseline else {}
    existing_files = (existing["manifest"].get("files") or {}) if existing else {}

    day_dir = chronicle_day_dir(map_name, day)
    os.makedirs(day_dir, exist_ok=True)

    captured_at = int(time.time())
    files: dict[str, dict] = {}
    missing: list[str] = []
    invalid: list[str] = []
    byte_count = 0

    for name in CHRONICLE_FILES:
        source = _source_path(map_name, name)
        if not os.path.exists(source):
            missing.append(name)
            continue

        with open(source, "rb") as fh:
            raw = fh.read()

        # Uploads are written non-atomically (data_routes uses a plain open+dump),
        # so a capture can catch a half-written file. The chronicle is the only
        # copy of this day, making such corruption permanent — refuse to store it.
        #
        # An empty or whitespace-only file is a torn read too: `open(...,"w")`
        # truncates before the writer produces any bytes. It is not valid JSON
        # either, but reject it explicitly so the intent survives. Empty JSON
        # *containers* are legitimate data here (zoc_overlays.json is often
        # `{}`) and must still be captured.
        if not raw.strip():
            logger.warning(
                "Chronicle skipping empty source '%s' for map '%s' on %s",
                name,
                map_name,
                day,
            )
            invalid.append(name)
            continue

        try:
            json.loads(raw)
        except (ValueError, UnicodeDecodeError):
            logger.warning(
                "Chronicle skipping unparsable source '%s' for map '%s' on %s",
                name,
                map_name,
                day,
            )
            invalid.append(name)
            continue

        sha = hashlib.sha256(raw).hexdigest()

        prior = previous_files.get(name)
        if previous_day and isinstance(prior, dict) and prior.get("sha256") == sha:
            # Unchanged since the last capture — point at it instead of copying.
            files[name] = {
                "sha256": sha,
                "same_as": prior.get("same_as") or previous_day,
                "bytes": len(raw),
            }
            continue

        current = existing_files.get(name)
        if (
            isinstance(current, dict)
            and current.get("sha256") == sha
            and not current.get("same_as")
            and os.path.exists(stored_file_path(map_name, day, name))
        ):
            # Re-capturing a day we already stored these exact bytes for (the
            # retry path below runs on every upload) — keep the entry rather
            # than re-compressing and rewriting identical content.
            files[name] = dict(current)
            byte_count += int(current.get("gzip_bytes") or 0)
            continue

        # mtime=0 keeps identical input byte-identical on disk, so ETags and
        # downstream caches stay stable.
        packed = gzip.compress(raw, mtime=0)
        _write_atomic(stored_file_path(map_name, day, name), packed)
        files[name] = {
            "sha256": sha,
            "bytes": len(raw),
            "gzip_bytes": len(packed),
        }
        byte_count += len(packed)

    manifest = {
        "map": map_name,
        "day": day,
        "captured_at": captured_at,
        "geometry_version": geometry_version(map_name),
        "files": files,
        "missing": missing,
        # Present on disk but unparsable — a torn read, not an absent source.
        "invalid": invalid,
    }
    _write_atomic(
        os.path.join(day_dir, "manifest.json"),
        json.dumps(manifest, indent=2, ensure_ascii=False).encode("utf-8"),
    )

    upsert_snapshot(
        map_id=map_name,
        day=day,
        realm_id=realm_for_map(map_name),
        captured_at=captured_at,
        byte_count=byte_count,
        geometry_version=manifest["geometry_version"],
        manifest=manifest,
    )
    return manifest


def capture_if_due(map_name: str) -> dict | None:
    """Capture unless today is already captured *completely*. Runs as a
    BackgroundTask, so it must never raise into the request that scheduled it.

    A row alone is not proof the day is safe: a source caught mid-rewrite is
    recorded as `invalid` and one caught before it was written as `missing`,
    and the row that records either would otherwise block every retry for the
    rest of the day — losing a file permanently even though good bytes are
    sitting on disk. So an incomplete manifest re-runs with force=True. That is
    safe by construction: no later day can point at today yet, which
    `_capture_locked` verifies anyway.
    """
    try:
        day = today_utc()
        # Take the lock once so the completeness decision and the capture it
        # implies cannot interleave with a concurrent capture of the same day.
        with _day_lock(map_name, day):
            existing = get_snapshot(map_name, day)
            if existing is not None and not _is_incomplete(existing["manifest"]):
                return None
            # A source that is absent for good re-runs once per upload forever;
            # that is accepted. The re-run only reads and hashes the sources —
            # unchanged bytes are kept by entry, not recompressed or rewritten.
            return _capture_locked(map_name, day, force=existing is not None)
    except Exception:
        logger.warning("Chronicle capture failed for map '%s'", map_name, exc_info=True)
        return None
