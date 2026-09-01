"""The cross-process map lock the chronicle/ledger destructive ops run under."""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
import threading
import time
from pathlib import Path

import pytest

_BACKEND_ROOT = Path(__file__).resolve().parents[3]
_BACKEND_SRC = _BACKEND_ROOT / "src"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

from src.scripts.util.maplock import MapLockBusy, map_lock  # noqa: E402


def test_non_blocking_acquire_refuses_a_held_lock(tmp_path: Path) -> None:
    path = str(tmp_path / "dev" / "chronicle.lock")
    held = threading.Event()
    release = threading.Event()
    busy: list[bool] = []

    def holder() -> None:
        with map_lock(path):
            held.set()
            release.wait(10)

    thread = threading.Thread(target=holder)
    thread.start()
    assert held.wait(10)
    try:
        with map_lock(path, blocking=False):
            busy.append(False)
    except MapLockBusy:
        busy.append(True)
    release.set()
    thread.join(10)

    assert busy == [True]
    # Free again once the holder let go.
    with map_lock(path, blocking=False):
        pass


def test_blocking_acquire_waits_for_the_holder(tmp_path: Path) -> None:
    path = str(tmp_path / "chronicle.lock")
    order: list[str] = []
    held = threading.Event()
    release = threading.Event()

    def holder() -> None:
        with map_lock(path):
            held.set()
            release.wait(10)
            order.append("holder-done")

    thread = threading.Thread(target=holder)
    thread.start()
    assert held.wait(10)

    waiter_in = threading.Event()

    def waiter() -> None:
        waiter_in.set()
        with map_lock(path, timeout=10):
            order.append("waiter-in")

    second = threading.Thread(target=waiter)
    second.start()
    assert waiter_in.wait(10)
    # Still blocked: nothing has been appended by the waiter.
    assert not any(entry == "waiter-in" for entry in order)

    release.set()
    thread.join(10)
    second.join(10)
    assert order == ["holder-done", "waiter-in"]


def test_blocking_acquire_gives_up_after_the_timeout(tmp_path: Path) -> None:
    """And after `timeout` in total, not twice it.

    The in-process RLock and the OS lock are two waits. Timing the second from a
    fresh clock let a caller asking for 0.5s block for 1.0s — for a threadpool
    worker, twice the time it is unavailable to serve anything else.
    """
    path = str(tmp_path / "chronicle.lock")
    held = threading.Event()
    release = threading.Event()

    def holder() -> None:
        with map_lock(path):
            held.set()
            release.wait(10)

    thread = threading.Thread(target=holder)
    thread.start()
    assert held.wait(10)
    started = time.monotonic()
    with pytest.raises(MapLockBusy):
        with map_lock(path, timeout=0.5):
            pass
    elapsed = time.monotonic() - started
    release.set()
    thread.join(10)

    assert 0.4 <= elapsed < 0.9, elapsed


def test_the_lock_is_reentrant_for_one_thread(tmp_path: Path) -> None:
    """`reindex_map` holds it across a loop whose body takes it again."""
    path = str(tmp_path / "ledger.lock")
    with map_lock(path):
        with map_lock(path, blocking=False):
            pass
        # The outer hold survives the inner release.
        assert os.path.isfile(path)
    with map_lock(path, blocking=False):
        pass


def test_the_lock_is_held_against_another_process(tmp_path: Path) -> None:
    """The whole point: a `threading.Lock` cannot see the second uvicorn worker."""
    path = tmp_path / "chronicle.lock"
    script = textwrap.dedent(
        f"""
        import sys
        sys.path.insert(0, {str(_BACKEND_ROOT)!r})
        sys.path.insert(0, {str(_BACKEND_SRC)!r})
        from src.scripts.util.maplock import MapLockBusy, map_lock
        try:
            with map_lock({str(path)!r}, blocking=False):
                print("acquired")
        except MapLockBusy:
            print("busy")
        """
    )
    with map_lock(str(path)):
        blocked = subprocess.run(
            [sys.executable, "-c", script], capture_output=True, text=True, timeout=60
        )
    free = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, timeout=60
    )

    assert blocked.stdout.strip() == "busy", blocked.stderr
    assert free.stdout.strip() == "acquired", free.stderr
