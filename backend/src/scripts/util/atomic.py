"""Crash-safe file writes and per-(scope, day) in-process locks.

Extracted from `scripts/chronicle/capture.py` unchanged so the ledger ingest can
reuse the same primitives; `capture` re-exports all three, so chronicle
behaviour and its tests' monkeypatch targets are untouched.
"""

from __future__ import annotations

import os
import tempfile
import threading

# Captures/ingests are scheduled on *every* upload and run synchronously in the
# threadpool, so several full runs for the same (map, day) can be in flight
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


def _write_atomic(path: str, data: bytes, prefix: str = ".chronicle-") -> None:
    """Write via a unique temp sibling so a crash never leaves a truncated file.

    The temp name must be unique, not a fixed `<path>.tmp`: a fixed sibling is
    atomic against a crash but not against a second writer, and two concurrent
    captures would either interleave into a corrupt file (POSIX) or raise
    PermissionError on the loser (Windows).
    """
    directory = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=prefix, suffix=".part")
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
