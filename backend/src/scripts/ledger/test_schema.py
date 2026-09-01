"""Payload normalisation: identity, partitioning, type tolerance, caps."""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

import pytest

from src.scripts.ledger.schema import (
    LedgerPayloadError,
    MAX_BREAKDOWN_KEYS,
    MAX_BREAKDOWN_KEY_CHARS,
    MAX_CAPTURED_AT_SKEW_SECONDS,
    MAX_FACTIONS,
    MAX_GUILDS,
    MAX_NESTING_DEPTH,
    MIN_CAPTURED_AT,
    faction_key,
    json_safe,
    normalize_snapshot,
    snapshot_day,
)

from .conftest import MAP, faction_payload, guild_payload, snapshot_payload


def test_faction_key_separates_id_from_founded_at() -> None:
    # Without the separator ("ab","c") and ("a","bc") would hash the same.
    assert faction_key("ab", "c") != faction_key("a", "bc")
    assert faction_key("alba", "x") == faction_key("alba", "x")


def test_same_id_different_founded_at_is_a_different_faction() -> None:
    reused = normalize_snapshot(
        snapshot_payload(
            factions=[
                faction_payload(founded_at="2026-01-01T00:00:00Z"),
                faction_payload(founded_at="2026-05-05T00:00:00Z"),
            ]
        ),
        MAP,
    )
    keys = {faction["key"] for faction in reused["factions"]}
    assert len(keys) == 2


def test_day_partitions_on_captured_at_not_server_day() -> None:
    snapshot = normalize_snapshot(
        snapshot_payload(captured_at="2026-09-01T23:59:59Z", server_day=999), MAP
    )
    assert snapshot["day"] == "2026-09-01"
    assert snapshot["server_day"] == 999

    # An offset instant partitions by its UTC date, not its local one.
    assert snapshot_day("2026-09-01T23:00:00-05:00") == "2026-09-02"


def test_complete_is_only_true_for_a_literal_true() -> None:
    for value in (False, None, 1, "true", "yes"):
        snapshot = normalize_snapshot(snapshot_payload(complete=value), MAP)
        assert snapshot["complete"] is False, value
    assert normalize_snapshot(snapshot_payload(complete=True), MAP)["complete"] is True


def test_rank_fields_are_read_the_java_way_round() -> None:
    snapshot = normalize_snapshot(snapshot_payload(), MAP)
    assert snapshot["factions"][0]["rank"] == "Kingdom"
    assert snapshot["factions"][0]["rank_level"] == 3


def test_swapped_rank_fields_are_tolerated_and_logged(caplog) -> None:
    """SF's own payload doc has these two the wrong way round."""
    swapped = snapshot_payload(
        factions=[faction_payload(rank=3, rank_level="Kingdom")]
    )
    with caplog.at_level("WARNING"):
        snapshot = normalize_snapshot(swapped, MAP)
    faction = snapshot["factions"][0]
    assert faction["rank"] == "Kingdom"
    assert faction["rank_level"] == 3
    assert any("numeric rank" in record.getMessage() for record in caplog.records)


def test_numeric_rank_without_a_string_counterpart_is_not_a_rank_name(caplog) -> None:
    """`rank: 3, rank_level: null` must not become the rank *named* "3"."""
    for level in (None, 3):
        payload = snapshot_payload(factions=[faction_payload(rank=3, rank_level=level)])
        caplog.clear()
        with caplog.at_level("WARNING"):
            faction = normalize_snapshot(payload, MAP)["factions"][0]
        assert faction["rank"] is None, level
        assert faction["rank_level"] == 3, level
        assert any(
            "numeric rank" in record.getMessage() for record in caplog.records
        ), level


def test_missing_identity_fields_are_refused() -> None:
    for bad in ({"founded_at": "x"}, {"id": "alba"}):
        with pytest.raises(LedgerPayloadError):
            normalize_snapshot(snapshot_payload(factions=[bad]), MAP)


def test_non_finite_numbers_become_null() -> None:
    snapshot = normalize_snapshot(
        snapshot_payload(
            factions=[
                faction_payload(
                    wealth=float("nan"),
                    prestige=float("inf"),
                    wealth_breakdown={"provinces": float("nan"), "trade": 1.0},
                )
            ]
        ),
        MAP,
    )
    faction = snapshot["factions"][0]
    assert faction["wealth"] is None
    assert faction["prestige"] is None
    # A poisoned breakdown entry is dropped, not zeroed.
    assert faction["wealth_breakdown"] == {"trade": 1.0}
    assert json_safe({"a": [math.inf, 1]}) == {"a": [None, 1]}


def test_unknown_keys_are_ignored_and_events_discarded() -> None:
    snapshot = normalize_snapshot(
        snapshot_payload(
            unheard_of_field=1,
            events=[{"type": "war"}],
            factions=[faction_payload(brand_new_metric=5)],
        ),
        MAP,
    )
    assert "unheard_of_field" not in snapshot
    assert "events" not in snapshot
    assert "brand_new_metric" not in snapshot["factions"][0]


def test_url_map_id_wins_over_the_payload_one() -> None:
    snapshot = normalize_snapshot(snapshot_payload(map_id="something-else"), MAP)
    assert snapshot["map_id"] == MAP
    assert snapshot["payload_map_id"] == "something-else"


def test_caps_are_refusals_not_truncation() -> None:
    too_many = [faction_payload(founded_at=str(i)) for i in range(MAX_FACTIONS + 1)]
    with pytest.raises(LedgerPayloadError) as excinfo:
        normalize_snapshot(snapshot_payload(factions=too_many), MAP)
    assert excinfo.value.status == 400

    with pytest.raises(LedgerPayloadError):
        normalize_snapshot(
            snapshot_payload(guilds=[guild_payload(id=str(i)) for i in range(MAX_GUILDS + 1)]),
            MAP,
        )


def test_bad_captured_at_is_a_payload_error() -> None:
    for bad in (None, "", "not-a-date", 17):
        with pytest.raises(LedgerPayloadError):
            normalize_snapshot(snapshot_payload(captured_at=bad), MAP)


def test_missing_collections_default_to_empty_on_a_partial_snapshot() -> None:
    """Only for `complete: false` — see the next test for why."""
    payload = snapshot_payload(complete=False)
    payload.pop("factions")
    payload.pop("guilds")
    payload.pop("global")
    snapshot = normalize_snapshot(payload, MAP)
    assert snapshot["factions"] == []
    assert snapshot["guilds"] == []
    assert snapshot["global"]["faction_wealth"] is None


def test_a_complete_snapshot_with_no_factions_key_is_refused() -> None:
    """A truncated POST loses its tail; that must not read as a server wipe."""
    payload = snapshot_payload()
    payload.pop("factions")
    with pytest.raises(LedgerPayloadError) as caught:
        normalize_snapshot(payload, MAP)
    assert "factions" in caught.value.detail
    assert caught.value.status == 400


def test_a_genuinely_empty_server_is_accepted_and_may_delete() -> None:
    """`factions: []` *present*, and the global count agrees: a real wipe."""
    payload = snapshot_payload(factions=[])
    payload["global"]["faction_count"] = 0
    snapshot = normalize_snapshot(payload, MAP)
    assert snapshot["factions"] == []
    assert snapshot["complete"] is True
    assert snapshot["deletion_safe"] is True


def test_faction_count_disagreeing_with_the_array_disarms_deletion() -> None:
    """A half-serialised array still indexes; it just may not delete."""
    payload = snapshot_payload(factions=[])
    payload["global"]["faction_count"] = 7
    snapshot = normalize_snapshot(payload, MAP)
    assert snapshot["complete"] is True
    assert snapshot["deletion_safe"] is False


def test_an_absent_faction_count_is_not_deletion_safe() -> None:
    """A complete snapshot with no `global.faction_count` may not delete.

    Genuine SF snapshots always carry the count. Treating its absence as
    "nothing to cross-check" made the cross-check opt-out: a hand-built LAN POST
    could drop `global` entirely and have every live faction stamped deleted.
    """
    payload = snapshot_payload()
    payload["global"].pop("faction_count")
    assert normalize_snapshot(payload, MAP)["deletion_safe"] is False


def test_a_snapshot_with_no_global_block_at_all_is_not_deletion_safe() -> None:
    payload = {
        "captured_at": "2026-09-01T12:00:00Z",
        "complete": True,
        "factions": [],
    }
    snapshot = normalize_snapshot(payload, MAP)
    # The day still indexes; only the deletions are refused.
    assert snapshot["day"] == "2026-09-01"
    assert snapshot["complete"] is True
    assert snapshot["deletion_safe"] is False


def test_an_incomplete_snapshot_is_never_deletion_safe() -> None:
    assert normalize_snapshot(snapshot_payload(complete=False), MAP)["deletion_safe"] is False


# --- captured_at bounds (finding 2) ------------------------------------------


def test_a_far_future_captured_at_is_refused() -> None:
    """One `9999-12-31` snapshot would become `days[-1]` and empty every chart.

    The default range clamps to the last MAX_RANGE_DAYS ending at the newest
    day, so every real day would fall outside it, and there is no per-day delete
    route to recover.
    """
    with pytest.raises(LedgerPayloadError) as excinfo:
        normalize_snapshot(snapshot_payload(captured_at="9999-12-31T00:00:00Z"), MAP)
    assert excinfo.value.status == 400
    assert "future" in excinfo.value.detail


def test_a_pre_epoch_captured_at_is_refused() -> None:
    before = MIN_CAPTURED_AT - timedelta(days=1)
    with pytest.raises(LedgerPayloadError):
        normalize_snapshot(
            snapshot_payload(captured_at=before.isoformat().replace("+00:00", "Z")), MAP
        )


def test_a_small_clock_skew_into_the_future_is_still_accepted() -> None:
    soon = datetime.now(timezone.utc) + timedelta(
        seconds=MAX_CAPTURED_AT_SKEW_SECONDS // 2
    )
    snapshot = normalize_snapshot(
        snapshot_payload(captured_at=soon.isoformat().replace("+00:00", "Z")), MAP
    )
    assert snapshot["day"] == soon.strftime("%Y-%m-%d")


# --- breakdown cardinality (finding 3) ---------------------------------------


def test_a_wide_breakdown_is_refused() -> None:
    """~200k keys fit in one 8 MiB body, and each becomes a full-length column."""
    wide = {f"k{i}": 1.0 for i in range(MAX_BREAKDOWN_KEYS + 1)}
    with pytest.raises(LedgerPayloadError) as excinfo:
        normalize_snapshot(
            snapshot_payload(factions=[faction_payload(wealth_breakdown=wide)]), MAP
        )
    assert str(MAX_BREAKDOWN_KEYS) in excinfo.value.detail


def test_a_long_breakdown_key_is_refused() -> None:
    long_key = {"x" * (MAX_BREAKDOWN_KEY_CHARS + 1): 1.0}
    with pytest.raises(LedgerPayloadError):
        normalize_snapshot(
            snapshot_payload(factions=[faction_payload(prestige_breakdown=long_key)]),
            MAP,
        )


def test_a_normal_breakdown_still_passes() -> None:
    snapshot = normalize_snapshot(snapshot_payload(), MAP)
    assert snapshot["factions"][0]["wealth_breakdown"] == {
        "provinces": 800.0,
        "trade": 200.0,
    }


# --- int range (finding 8) ---------------------------------------------------


def test_an_int_past_sqlite_range_is_dropped_not_stored() -> None:
    """sqlite3 raises OverflowError past 2^63, inside the background promote.

    That runs after the POST answered 200, so the day would be permanently and
    silently unindexed.
    """
    payload = snapshot_payload(factions=[faction_payload(members=2**63)])
    payload["global"]["population"] = -(2**63) - 1
    snapshot = normalize_snapshot(payload, MAP)
    assert snapshot["factions"][0]["members"] is None
    assert snapshot["global"]["population"] is None


def test_an_int_at_the_sqlite_boundary_survives() -> None:
    snapshot = normalize_snapshot(
        snapshot_payload(factions=[faction_payload(members=2**63 - 1)]), MAP
    )
    assert snapshot["factions"][0]["members"] == 2**63 - 1


# --- nesting depth (finding 10) ----------------------------------------------


def test_a_deeply_nested_payload_is_refused_not_a_recursion_error() -> None:
    nested: object = []
    for _ in range(MAX_NESTING_DEPTH + 5):
        nested = [nested]
    with pytest.raises(LedgerPayloadError):
        normalize_snapshot(
            snapshot_payload(factions=[faction_payload(wars=[nested])]), MAP
        )
