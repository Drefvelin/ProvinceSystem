"""Upload-route tests for the ledger branch, and the regression that guards
every other mode's on-disk bytes.

The app is assembled from `data_router` alone rather than imported from
`server` — see the note in `test_ledger_routes.py`.
"""

from __future__ import annotations

import gzip
import json
import os
import sys
from pathlib import Path

import pytest

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_SRC = _BACKEND_ROOT / "src"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

os.environ.setdefault("SKINS_DEV", "1")

from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from src.api.data_routes import data_router  # noqa: E402
from src.api.map_registry import clear_map_registry_cache  # noqa: E402
from src.scripts.chronicle import capture as chronicle_capture  # noqa: E402
from src.scripts.ledger import store  # noqa: E402
from src.scripts.ledger.schema import faction_key  # noqa: E402
from src.scripts.util import dirs  # noqa: E402
from src.skins import db as skins_db  # noqa: E402

TEST_REGISTRY = """
maps:
  - id: main
    public: true
    display_name: Adavaar
    realm_id: main
  - id: dev
    public: false
    display_name: Adavaar
    realm_id: dev
    staff_permission: tfmc.map.staff
"""

ALBA_KEY = faction_key("alba", "2026-01-01T00:00:00Z")

LOCALHOST = ("127.0.0.1", 12345)


def _faction(**overrides) -> dict:
    faction = {
        "id": "alba",
        "founded_at": "2026-01-01T00:00:00Z",
        "name": "Alba",
        "rgb": "#ff0000",
        "overlord": None,
        "subjects": [],
        "wealth": 1000.0,
        "wealth_breakdown": {"provinces": 800.0},
        "bank": 100.0,
        "vassal_wealth": 0.0,
        "net_income": 12.5,
        "inflation_delta": -0.5,
        "trade_power": 7.0,
        "prestige": 500.0,
        "prestige_breakdown": {"wealth": 300.0},
        "rank": "Kingdom",
        "rank_level": 3,
        "rank_up_at": 600.0,
        "rank_down_at": 400.0,
        "prestige_position": 1,
        "wealth_position": 1,
        "provinces": 12,
        "realm_size": 12,
        "tier": "king",
        "tier_index": 4,
        "highest_title": "King of Alba",
        "members": 5,
        "members_with_vassals": 5,
        "settlements": 3,
        "population": 340,
        "installations": 2,
        "forts": 1,
        "wars": [],
    }
    faction.update(overrides)
    return faction


def _snapshot(**overrides) -> dict:
    payload = {
        "schema_version": 1,
        "map_id": "main",
        "captured_at": "2026-09-01T12:00:00Z",
        "server_day": 41,
        "day_progress_seconds": 900,
        "complete": True,
        "global": {"faction_count": 1, "faction_wealth": 1000.0},
        "factions": [_faction()],
        "guilds": [],
        "events": [],
    }
    payload.update(overrides)
    # `global.faction_count` tracks the array unless a test overrides `global`:
    # the two disagreeing is exactly what disarms deletions on the ingest side.
    if "global" not in overrides:
        payload["global"]["faction_count"] = len(payload.get("factions") or [])
    return payload


@pytest.fixture
def upload_env(tmp_path, monkeypatch):
    registry = tmp_path / "maps.yml"
    registry.write_text(TEST_REGISTRY, encoding="utf-8")
    monkeypatch.setenv("MAP_REGISTRY_PATH", str(registry))
    clear_map_registry_cache()

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    monkeypatch.setattr(skins_db, "DATA_DIR", data_dir)
    monkeypatch.setattr(skins_db, "DB_PATH", data_dir / "province.db")
    monkeypatch.setattr(skins_db, "SKINS_DIR", data_dir / "skins")
    monkeypatch.setattr(skins_db, "WARDROBE_DIR", data_dir / "wardrobe")
    monkeypatch.setattr(skins_db, "DRINKS_DIR", data_dir / "drinks")

    monkeypatch.setattr(dirs, "INPUT_DIR", str(tmp_path / "input"))
    monkeypatch.setattr(dirs, "DEFINES_DIR", str(tmp_path / "defines"))
    monkeypatch.setattr(store, "OUTPUT_DIR", str(tmp_path / "output"))

    # The daily timelapse capture rides the upload; it reads the real defines
    # tree and is not what these tests are about.
    captures: list[str] = []
    monkeypatch.setattr(
        chronicle_capture, "capture_if_due", lambda map_name: captures.append(map_name)
    )
    monkeypatch.setattr(
        "src.api.data_routes.generate_zoc_overlays", lambda map_name: None
    )
    monkeypatch.setattr(
        "src.api.data_routes.create_infestation_map", lambda map_name: None
    )

    skins_db.migrate()
    try:
        yield {"root": tmp_path, "captures": captures}
    finally:
        clear_map_registry_cache()


@pytest.fixture
def client(upload_env):
    app = FastAPI()
    app.include_router(data_router)
    with TestClient(app, client=LOCALHOST) as test_client:
        yield test_client


# --- regression: existing modes keep byte-identical on-disk behaviour ---------


def _expected_bytes(payload: object) -> str:
    """Exactly what the pre-ledger handler wrote: json.dump(..., indent=2)."""
    return json.dumps(payload, ensure_ascii=False, indent=2)


def test_input_mode_bytes_are_unchanged(client, upload_env):
    """`nation` is an `input/` mode — same path, same bytes, same side effects."""
    payload = {"nations": [{"id": "alba", "name": "Álba", "wealth": 1.5}]}
    res = client.post("/main/data/upload/nation", json=payload)
    assert res.status_code == 200
    assert res.json() == {"message": "nation data saved for 'main'"}

    path = upload_env["root"] / "input" / "main" / "nation.json"
    assert path.read_text(encoding="utf-8") == _expected_bytes(payload)
    # The legacy path resolves the map from the raw segment, not the registry.
    assert upload_env["captures"] == ["main"]


def test_defines_mode_bytes_are_unchanged(client, upload_env):
    """`zoc_overlays` is an unknown mode, so it falls through to `defines/`."""
    payload = {"forts": {"f1": {"url": "/x.png"}}}
    res = client.post("/main/data/upload/zoc_overlays", json=payload)
    assert res.status_code == 200
    assert res.json() == {"message": "zoc_overlays data saved for 'main'"}

    path = upload_env["root"] / "defines" / "main" / "zoc_overlays.json"
    assert path.read_text(encoding="utf-8") == _expected_bytes(payload)


def test_ledger_mode_writes_no_defines_file(client, upload_env):
    client.post("/main/data/upload/chronicle", json=_snapshot())
    assert not (upload_env["root"] / "defines" / "main" / "chronicle.json").exists()


# --- ledger branch -----------------------------------------------------------


def test_ledger_upload_stores_raw_and_promotes(client, upload_env):
    res = client.post("/main/data/upload/chronicle", json=_snapshot())
    assert res.status_code == 200
    body = res.json()
    assert body["map"] == "main"
    assert body["day"] == "2026-09-01"
    assert body["captured_at"] == "2026-09-01T12:00:00Z"
    assert body["complete"] is True
    assert body["factions"] == 1

    raw_dir = upload_env["root"] / "output" / "main" / "ledger" / "raw" / "2026-09-01"
    assert len(list(raw_dir.glob("*.json.gz"))) == 1

    daily = upload_env["root"] / "output" / "main" / "ledger" / "daily" / "2026-09-01.json.gz"
    assert daily.exists()
    stored = json.loads(gzip.decompress(daily.read_bytes()))
    assert stored["day"] == "2026-09-01"
    assert store.list_days("main")[0]["day"] == "2026-09-01"


def test_two_snapshots_in_one_day_keep_both_raw_files(client, upload_env):
    client.post("/main/data/upload/chronicle", json=_snapshot())
    client.post(
        "/main/data/upload/chronicle",
        json=_snapshot(captured_at="2026-09-01T12:05:00Z"),
    )

    raw_dir = upload_env["root"] / "output" / "main" / "ledger" / "raw" / "2026-09-01"
    assert len(list(raw_dir.glob("*.json.gz"))) == 2
    assert [row["day"] for row in store.list_days("main")] == ["2026-09-01"]


def test_capture_if_due_still_runs_last_on_the_ledger_branch(client, upload_env):
    client.post("/main/data/upload/chronicle", json=_snapshot())
    # Queued behind the promote, and keyed off the URL segment like every
    # other mode - see the next test.
    assert upload_env["captures"] == ["main"]


def test_a_mixed_case_url_captures_under_the_url_segment(client, upload_env):
    """The timelapse must not fork a second series under the normalised id.

    `capture_if_due` reads `input_file(<name>, ...)`/`defines_file(<name>, ...)`,
    and every other upload mode writes those under the raw URL segment. Handing
    it the registry id instead would start a chronicle for a map whose sources
    do not exist there - a permanently-incomplete manifest, retried on every
    upload forever. The ledger rows still key off the registry id.
    """
    res = client.post("/Main/data/upload/chronicle", json=_snapshot())
    assert res.status_code == 200
    assert res.json()["map"] == "main"
    assert upload_env["captures"] == ["Main"]
    # Storage is unaffected: still one series, under the registry id.
    assert [row["day"] for row in store.list_days("main")] == ["2026-09-01"]


def test_incomplete_snapshot_never_marks_a_deletion(client, upload_env):
    client.post("/main/data/upload/chronicle", json=_snapshot())
    client.post(
        "/main/data/upload/chronicle",
        json=_snapshot(
            captured_at="2026-09-02T12:00:00Z", complete=False, factions=[]
        ),
    )

    rows = store.list_registry("main")
    assert [row["deleted_day"] for row in rows] == [None]


def test_complete_snapshot_marks_absence_as_deletion(client, upload_env):
    client.post("/main/data/upload/chronicle", json=_snapshot())
    client.post(
        "/main/data/upload/chronicle",
        json=_snapshot(captured_at="2026-09-02T12:00:00Z", factions=[]),
    )

    (row,) = store.list_registry("main")
    assert row["faction_key"] == ALBA_KEY
    assert row["deleted_day"] == "2026-09-02"


def test_reused_id_with_a_new_founded_at_is_a_separate_identity(client, upload_env):
    client.post("/main/data/upload/chronicle", json=_snapshot())
    client.post(
        "/main/data/upload/chronicle",
        json=_snapshot(
            captured_at="2026-09-02T12:00:00Z",
            factions=[_faction(founded_at="2026-06-01T00:00:00Z")],
        ),
    )

    keys = {row["faction_key"] for row in store.list_registry("main")}
    assert len(keys) == 2
    assert ALBA_KEY in keys


def test_partition_is_on_captured_at_not_server_day(client, upload_env):
    """Two snapshots with the same `server_day` but different UTC dates split."""
    client.post("/main/data/upload/chronicle", json=_snapshot(server_day=41))
    client.post(
        "/main/data/upload/chronicle",
        json=_snapshot(captured_at="2026-09-02T00:30:00Z", server_day=41),
    )

    assert [row["day"] for row in store.list_days("main")] == [
        "2026-09-01",
        "2026-09-02",
    ]


def test_map_id_mismatch_against_an_unknown_name_is_accepted(client, upload_env):
    res = client.post(
        "/main/data/upload/chronicle", json=_snapshot(map_id="Adavaar-Overworld")
    )
    assert res.status_code == 200
    assert res.json()["map"] == "main"
    assert store.list_days("main")


def test_map_id_case_difference_is_accepted(client, upload_env):
    res = client.post("/main/data/upload/chronicle", json=_snapshot(map_id="MAIN"))
    assert res.status_code == 200
    assert res.json()["map"] == "main"


def test_map_id_naming_a_different_registered_map_is_409(client, upload_env):
    res = client.post("/main/data/upload/chronicle", json=_snapshot(map_id="dev"))
    assert res.status_code == 409
    assert not store.list_days("main")


def test_unknown_map_on_the_ledger_branch_is_404(client, upload_env):
    res = client.post("/nosuchmap/data/upload/chronicle", json=_snapshot())
    assert res.status_code == 404


def test_bad_snapshot_is_400_and_writes_nothing(client, upload_env):
    res = client.post(
        "/main/data/upload/chronicle", json=_snapshot(captured_at="not-a-date")
    )
    assert res.status_code == 400
    assert not (upload_env["root"] / "output" / "main").exists()


def test_faction_without_founded_at_is_400(client, upload_env):
    faction = _faction()
    faction.pop("founded_at")
    res = client.post("/main/data/upload/chronicle", json=_snapshot(factions=[faction]))
    assert res.status_code == 400


def test_non_localhost_upload_is_403(upload_env):
    app = FastAPI()
    app.include_router(data_router)
    with TestClient(app, client=LOCALHOST) as remote:
        res = remote.post(
            "/main/data/upload/chronicle",
            json=_snapshot(),
            headers={"X-Forwarded-For": "8.8.8.8"},
        )
    assert res.status_code == 403


# --- body reader -------------------------------------------------------------


def test_oversize_ledger_body_is_413(client, upload_env, monkeypatch):
    monkeypatch.setattr("src.api.data_routes.LEDGER_MAX_BODY_BYTES", 64)
    res = client.post("/main/data/upload/chronicle", json=_snapshot())
    assert res.status_code == 413
    assert not (upload_env["root"] / "output" / "main").exists()


def test_oversize_legacy_body_is_413(client, upload_env, monkeypatch):
    monkeypatch.setattr("src.api.data_routes.UPLOAD_MAX_BODY_BYTES", 8)
    res = client.post("/main/data/upload/nation", json={"nations": [1, 2, 3]})
    assert res.status_code == 413
    assert not (upload_env["root"] / "input" / "main").exists()


def test_malformed_json_is_400_not_500(client, upload_env):
    res = client.post(
        "/main/data/upload/chronicle",
        content=b"{not json",
        headers={"content-type": "application/json"},
    )
    assert res.status_code == 400


def test_legacy_mode_malformed_json_is_400_not_500(client, upload_env):
    res = client.post(
        "/main/data/upload/nation",
        content=b"",
        headers={"content-type": "application/json"},
    )
    assert res.status_code == 400


def test_deeply_nested_json_is_400_not_500(client, upload_env):
    """`json.loads` raises RecursionError, not ValueError, on deep nesting.

    The reader caught only ValueError, so 8 MiB of `[[[[…]]]]` surfaced as a
    500 from an unhandled exception rather than the 400 it is.
    """
    depth = 20000
    body = ("[" * depth) + ("]" * depth)
    res = client.post(
        "/main/data/upload/chronicle",
        content=body.encode("ascii"),
        headers={"content-type": "application/json"},
    )
    assert res.status_code == 400


def test_a_far_future_captured_at_is_refused_by_the_upload(client, upload_env):
    """Finding 2, end to end: nothing is stored and no day is indexed."""
    payload = _snapshot()
    payload["captured_at"] = "9999-12-31T00:00:00Z"

    res = client.post("/main/data/upload/chronicle", json=payload)

    assert res.status_code == 400
    assert store.list_days("main") == []  # nothing indexed
