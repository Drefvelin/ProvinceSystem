"""Crash-safe file writes, tree renames, and per-(scope, day) in-process locks.

`_day_lock`, `_fsync_dir` and `_write_atomic` were extracted from
`scripts/chronicle/capture.py` unchanged so the ledger ingest could reuse the
same primitives; `capture` re-exports all three, so chronicle behaviour and its
tests' monkeypatch targets are untouched. `rename_aside` was extracted from the
chronicle wipe for the same reason: the ledger wipe makes the identical
"renamed aside" promise and used to break it the identical way.
"""

from __future__ import annotations

import errno
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


def _read_umask() -> int:
    """The process umask, without permanently changing it.

    `os.umask()` has no query-only mode — the only way to read it is to set a
    throwaway value and restore the old one, which is itself a tiny race
    against a concurrent thread doing the same. Reading it once at import time
    (the umask essentially never changes after process start) avoids paying
    that race on every single write.
    """
    try:
        old = os.umask(0)
        os.umask(old)
        return old
    except (AttributeError, OSError):
        return 0


_UMASK = _read_umask()


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
        # mkstemp creates the file 0600 regardless of the process umask, so
        # every artifact written through here would otherwise land owner-only
        # instead of matching the permissions a normal `open(...).write()`
        # would have produced. Best-effort: a chmod failure (e.g. a
        # filesystem that doesn't support the bits) must not lose the write.
        try:
            os.chmod(tmp, 0o666 & ~_UMASK)
        except OSError:
            pass
        os.replace(tmp, path)
        tmp = None
    finally:
        if tmp is not None:
            try:
                os.unlink(tmp)
            except OSError:
                pass
    _fsync_dir(directory)


class CrossDeviceError(RuntimeError):
    """A set-aside rename that would have to become a copy. Operator-readable."""


def rename_aside(source: str, destination: str) -> None:
    """Move a whole tree aside by renaming it, or refuse. Never a copy.

    `shutil.move` silently degrades to copytree+rmtree across a device boundary,
    which is not what a "renamed aside" backup promises: it doubles the disk
    footprint of the tree, takes unbounded time while the map lock is held, and
    deletes the original afterwards, so a failure part-way through leaves the
    days split across two trees. An operator who has put the output directory on
    a different filesystem from its backups needs to hear about it rather than
    have the wipe quietly become a copy.

    Shared by the chronicle and ledger wipes: both rename `<root>` to
    `<root>.bak.<stamp>` and both made the same promise.
    """
    try:
        os.rename(source, destination)
    except OSError as exc:
        if exc.errno == errno.EXDEV:
            raise CrossDeviceError(
                f"Cannot set aside {source}: the backup path {destination} is on a "
                "different filesystem, and setting aside only ever renames. Put the "
                "map's output directory and its backups on the same filesystem."
            ) from exc
        raise
