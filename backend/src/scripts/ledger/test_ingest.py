"""Raw snapshot storage layout and the atomic-write primitives it borrows."""

from __future__ import annotations

import gzip
import json
import os
from pathlib import Path

from src.scripts.chronicle import capture as capture_mod
from src.scripts.ledger import ingest, store
from src.scripts.ledger.schema import normalize_snapshot
from src.scripts.util import atomic

from .conftest import MAP, faction_payload, snapshot_payload


def _store(env: Path, **overrides) -> str:
    snapshot = normalize_snapshot(snapshot_payload(**overrides), MAP)
    return ingest.store_raw(MAP, snapshot)


def test_raw_path_partitions_on_the_captured_at_utc_date(env: Path) -> None:
    path = _store(env, captured_at="2026-09-01T23:30:05Z", server_day=999)

    assert Path(path).parent == Path(store.raw_day_dir(MAP, "2026-09-01"))
    assert Path(path).name.startswith("233005Z-")
    assert path.endswith(".json.gz")


def test_offset_instant_lands_in_the_utc_day(env: Path) -> None:
    path = _store(env, captured_at="2026-09-01T23:00:00-05:00")
    assert Path(path).parent.name == "2026-09-02"
    assert Path(path).name.startswith("040000Z-")


def test_two_snapshots_in_one_second_stay_distinct(env: Path) -> None:
    first = _store(env, captured_at="2026-09-01T12:00:00Z", server_day=1)
    second = _store(env, captured_at="2026-09-01T12:00:00Z", server_day=2)

    assert first != second
    assert len(os.listdir(store.raw_day_dir(MAP, "2026-09-01"))) == 2


def test_identical_retry_overwrites_itself(env: Path) -> None:
    first = _store(env)
    second = _store(env)

    assert first == second
    assert len(os.listdir(store.raw_day_dir(MAP, "2026-09-01"))) == 1


def test_raw_body_round_trips_and_is_json_clean(env: Path) -> None:
    path = _store(env, factions=[faction_payload(wealth=float("nan"))])

    body = json.loads(gzip.decompress(Path(path).read_bytes()))
    assert body["factions"][0]["wealth"] is None
    # gzip mtime=0 keeps identical content byte-identical on disk.
    assert Path(path).read_bytes() == gzip.compress(
        json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode(),
        mtime=0,
    )


def test_no_temp_siblings_survive_a_write(env: Path) -> None:
    _store(env)
    day_dir = Path(store.raw_day_dir(MAP, "2026-09-01"))
    assert [p.name for p in day_dir.iterdir() if ".part" in p.name] == []


def test_atomic_helpers_are_shared_with_chronicle_not_copied() -> None:
    """capture.py re-exports them; two copies would drift."""
    assert capture_mod._write_atomic is atomic._write_atomic
    assert capture_mod._day_lock is atomic._day_lock
    assert capture_mod._fsync_dir is atomic._fsync_dir


def test_ledger_and_chronicle_day_locks_do_not_collide() -> None:
    assert ingest._day_lock(f"ledger:{MAP}", "2026-09-01") is not ingest._day_lock(
        MAP, "2026-09-01"
    )


def test_prune_raw_is_available_but_never_called(env: Path) -> None:
    """Retention is keep-everything; the helper exists for later ops only."""
    for day in ("2026-08-30", "2026-08-31", "2026-09-01"):
        _store(env, captured_at=f"{day}T12:00:00Z")

    ingest.promote_day(MAP, "2026-09-01")
    assert sorted(os.listdir(store.raw_root(MAP))) == [
        "2026-08-30",
        "2026-08-31",
        "2026-09-01",
    ]

    assert ingest.prune_raw(MAP, keep_days=2) == ["2026-08-30"]
    assert sorted(os.listdir(store.raw_root(MAP))) == ["2026-08-31", "2026-09-01"]
