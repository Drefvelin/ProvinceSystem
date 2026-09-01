"""Guard tests for the spoof-ledger seeder.

Only the refusal path is covered: everything below it writes synthetic economy
history through the real `store_raw` + `promote_day` stack, which is exercised
by `src/scripts/ledger/test_ingest.py`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pytest

_BACKEND_ROOT = Path(__file__).resolve().parents[3]
_BACKEND_SRC = _BACKEND_ROOT / "src"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

from src.api.map_registry import clear_map_registry_cache  # noqa: E402
from src.scripts.tools import generate_spoof_ledger as spoof  # noqa: E402

TEST_REGISTRY = """
maps:
  - id: main
    public: true
    display_name: Adavaar
    realm_id: main
  - id: r3b1rth
    public: true
    display_name: Rebirth
    realm_id: r3b1rth
  - id: dev
    public: false
    display_name: Adavaar
    realm_id: dev
    staff_permission: tfmc.map.staff
"""


@pytest.fixture
def registry(tmp_path, monkeypatch):
    path = tmp_path / "maps.yml"
    path.write_text(TEST_REGISTRY, encoding="utf-8")
    monkeypatch.setenv("MAP_REGISTRY_PATH", str(path))
    clear_map_registry_cache()
    try:
        yield
    finally:
        clear_map_registry_cache()


@pytest.fixture
def parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(prog="generate_spoof_ledger")


def _no_existing_days(monkeypatch, days):
    monkeypatch.setattr(spoof, "existing_ledger_days", lambda map_id: days)


@pytest.mark.parametrize("map_id", ["main", "r3b1rth"])
def test_public_map_is_refused(registry, parser, monkeypatch, map_id):
    """Every public map, not just the hardcoded 'main' the old guard knew."""
    _no_existing_days(monkeypatch, [])
    with pytest.raises(SystemExit):
        spoof.guard_target_map(parser, map_id, force=False)


@pytest.mark.parametrize("map_id", ["main", "r3b1rth"])
def test_force_does_not_unlock_a_public_map(registry, parser, monkeypatch, map_id):
    _no_existing_days(monkeypatch, [])
    with pytest.raises(SystemExit):
        spoof.guard_target_map(parser, map_id, force=True)


def test_empty_staff_map_is_allowed(registry, parser, monkeypatch):
    _no_existing_days(monkeypatch, [])
    spoof.guard_target_map(parser, "dev", force=False)


def test_unreadable_index_does_not_demand_force(registry, parser, monkeypatch):
    """No database yet is not "has history"; seeding a fresh map stays one command."""
    _no_existing_days(monkeypatch, None)
    spoof.guard_target_map(parser, "dev", force=False)


def test_staff_map_with_existing_days_needs_force(registry, parser, monkeypatch):
    _no_existing_days(monkeypatch, ["2026-01-01", "2026-01-02"])
    with pytest.raises(SystemExit):
        spoof.guard_target_map(parser, "dev", force=False)


def test_force_allows_a_staff_map_with_existing_days(registry, parser, monkeypatch):
    _no_existing_days(monkeypatch, ["2026-01-01", "2026-01-02"])
    spoof.guard_target_map(parser, "dev", force=True)


def test_describe_target_names_the_map_and_days(registry, capsys):
    payloads = [{"day": "2026-01-01"}, {"day": "2026-01-02"}]
    spoof.describe_target("dev", payloads, post=False)
    out = capsys.readouterr().out
    assert "'dev'" in out
    assert "staff-only" in out
    assert "2026-01-01 .. 2026-01-02" in out
