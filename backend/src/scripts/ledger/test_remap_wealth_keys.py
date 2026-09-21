"""Daily rewrite CLI: colored guild wealth keys become guild ids."""

from __future__ import annotations

import gzip
import json
from pathlib import Path

from src.scripts.ledger import ingest, remap_wealth_keys, store
from src.scripts.ledger.schema import normalize_snapshot

from .conftest import MAP, faction_payload, guild_payload, snapshot_payload
from .test_schema import _COLORED_GUILD_KEY

DAY = "2026-09-01"


def _write_daily_with_colored_key(env: Path) -> dict:
    """Promote a snapshot, then put the pre-remap keys back on the daily file.

    Ingest remaps on the way in, so a real stored day after this change would
    already be ids. The CLI exists for days written by the old path.
    """
    snapshot = normalize_snapshot(
        snapshot_payload(
            captured_at=f"{DAY}T12:00:00Z",
            factions=[
                faction_payload(
                    wealth_breakdown={"Bank": 1.0, "The_Betriebsrat": 2.0}
                )
            ],
            guilds=[
                guild_payload(
                    id="The_Betriebsrat",
                    faction_id="alba",
                    name="§x§a§3§a§1§8§4The Betriebsrat",
                    type="§x§b§d§a§4§6§4Guild",
                )
            ],
        ),
        MAP,
    )
    ingest.store_raw(MAP, snapshot)
    ingest.promote_day(MAP, DAY)

    snapshot["factions"][0]["wealth_breakdown"] = {
        "Bank": 1.0,
        _COLORED_GUILD_KEY: 2.0,
    }
    path = store.daily_path(MAP, DAY)
    packed = ingest._pack(snapshot)
    Path(path).write_bytes(packed)
    return snapshot


def _read_daily() -> dict:
    with gzip.open(store.daily_path(MAP, DAY), "rb") as fh:
        return json.loads(fh.read())


def test_dry_run_does_not_rewrite(env: Path) -> None:
    _write_daily_with_colored_key(env)
    assert remap_wealth_keys.remap_map(MAP, dry_run=True) == 0
    daily = _read_daily()
    assert _COLORED_GUILD_KEY in daily["factions"][0]["wealth_breakdown"]


def test_rewrite_replaces_colored_keys_on_daily(env: Path) -> None:
    _write_daily_with_colored_key(env)
    assert remap_wealth_keys.remap_map(MAP) == 0
    daily = _read_daily()
    assert daily["factions"][0]["wealth_breakdown"] == {
        "Bank": 1.0,
        "The_Betriebsrat": 2.0,
    }


def test_rewrite_is_a_noop_when_keys_are_already_ids(env: Path) -> None:
    snapshot = normalize_snapshot(
        snapshot_payload(
            captured_at=f"{DAY}T12:00:00Z",
            factions=[
                faction_payload(
                    wealth_breakdown={"Bank": 1.0, "The_Betriebsrat": 2.0}
                )
            ],
            guilds=[
                guild_payload(
                    id="The_Betriebsrat",
                    faction_id="alba",
                    name="§x§a§3§a§1§8§4The Betriebsrat",
                    type="§x§b§d§a§4§6§4Guild",
                )
            ],
        ),
        MAP,
    )
    ingest.store_raw(MAP, snapshot)
    ingest.promote_day(MAP, DAY)
    before = Path(store.daily_path(MAP, DAY)).read_bytes()
    assert remap_wealth_keys.remap_map(MAP) == 0
    assert Path(store.daily_path(MAP, DAY)).read_bytes() == before
