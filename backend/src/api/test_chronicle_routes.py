"""API tests for the chronicle read routes and the localhost capture trigger."""

from __future__ import annotations

import gzip
import json
import os
import sys
import time
from pathlib import Path

import pytest

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_SRC = _BACKEND_ROOT / "src"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

os.environ.setdefault("SKINS_DEV", "1")

from fastapi.testclient import TestClient  # noqa: E402

from src.api.map_registry import clear_map_registry_cache  # noqa: E402
from src.scripts.chronicle import store  # noqa: E402
from src.skins import db as skins_db  # noqa: E402
from server import app  # noqa: E402

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


@pytest.fixture
def chronicle_env(tmp_path, monkeypatch):
    """Point the chronicle at a throwaway output dir and SQLite file.

    Everything the routes touch — day folders and the index table — has to live
    under tmp_path; the real src/output and src/data/province.db must never be
    written by a test run.
    """
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

    output_dir = tmp_path / "output"
    monkeypatch.setattr(store, "OUTPUT_DIR", str(output_dir))

    skins_db.migrate()
    try:
        yield tmp_path
    finally:
        clear_map_registry_cache()


@pytest.fixture
def client(chronicle_env):
    with TestClient(app) as test_client:
        yield test_client


def _write_day(map_name: str, day: str, name: str, payload: object) -> None:
    path = store.stored_file_path(map_name, day, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        json.dump(payload, handle)
    store.upsert_snapshot(
        map_name,
        day,
        "main",
        int(time.time()),
        os.path.getsize(path),
        None,
        {"files": {name: {"sha256": "x", "bytes": os.path.getsize(path)}}},
    )


def test_index_without_snapshots_is_empty_not_error(client):
    res = client.get("/main/chronicle/index")
    assert res.status_code == 200
    body = res.json()
    assert body["days"] == []
    assert body["first"] is None
    assert body["last"] is None


def test_index_lists_days_ascending(client):
    _write_day("main", "2026-01-01", "nation", {"a": 1})
    _write_day("main", "2026-01-02", "nation", {"a": 2})

    body = client.get("/main/chronicle/index").json()
    assert body["days"] == ["2026-01-01", "2026-01-02"]
    assert body["first"] == "2026-01-01"
    assert body["last"] == "2026-01-02"


def test_data_route_serves_gzip_bytes(client):
    _write_day("main", "2026-01-01", "nation", {"a": 1})

    res = client.get("/main/chronicle/2026-01-01/data/nation")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/gzip"
    # httpx does not transparently decode application/gzip, exactly as the
    # browser does not — the client is expected to gunzip it itself.
    assert json.loads(gzip.decompress(res.content)) == {"a": 1}


def test_missing_snapshot_is_404(client):
    res = client.get("/main/chronicle/2026-01-01/data/nation")
    assert res.status_code == 404


@pytest.mark.parametrize(
    "name",
    ["../../secret", "manifest", "nation.json", "..", "queue"],
)
def test_bad_file_name_is_rejected_without_touching_disk(client, monkeypatch, name):
    def _boom(*args, **kwargs):  # pragma: no cover - must never run
        raise AssertionError("filesystem reached with an unvalidated name")

    monkeypatch.setattr(store, "resolve_stored_file", _boom)
    monkeypatch.setattr("src.api.chronicle_routes.resolve_stored_file", _boom)

    res = client.get(f"/main/chronicle/2026-01-01/data/{name}")
    assert res.status_code in (400, 404)
    if res.status_code == 400:
        assert "Unknown chronicle file" in res.json()["detail"]


@pytest.mark.parametrize("day", ["nope", "2026-13-01", "2026-1-1", "../../etc"])
def test_bad_day_is_rejected(client, day):
    res = client.get(f"/main/chronicle/{day}/data/nation")
    assert res.status_code in (400, 404)


def test_dev_map_requires_staff_but_main_is_public(client):
    assert client.get("/dev/chronicle/index").status_code == 403
    assert client.get("/main/chronicle/index").status_code == 200


def test_snapshot_post_rejects_non_localhost(client):
    res = client.post(
        "/main/chronicle/snapshot",
        headers={"X-Forwarded-For": "8.8.8.8"},
    )
    assert res.status_code == 403


def test_snapshot_post_from_localhost_schedules_capture(chronicle_env, monkeypatch):
    calls: list[tuple] = []
    monkeypatch.setattr(
        "src.scripts.chronicle.capture.capture_snapshot",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )
    with TestClient(app, client=("127.0.0.1", 12345)) as test_client:
        res = test_client.post("/main/chronicle/snapshot?force=true")

    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["map"] == "main"
    assert body["force"] is True
    assert calls == [(("main", None, True), {})]


@pytest.fixture
def defines_dir(chronicle_env, monkeypatch):
    """Empty stand-in for src/defines so artifact presence is under test control."""
    root = chronicle_env / "defines"

    def _defines_file(map_name: str, filename: str) -> str:
        return str(root / map_name / filename)

    monkeypatch.setattr("src.api.data_routes.defines_file", _defines_file)
    return root


@pytest.mark.parametrize(
    "route, filename",
    [
        ("province_id_runs", "province_id_runs.bin.gz"),
        ("province_id_grid_q4", "province_id_grid_q4.bin.gz"),
    ],
)
def test_public_artifact_routes_404_without_artifact(client, defines_dir, route, filename):
    res = client.get(f"/main/data/{route}")
    assert res.status_code == 404
    assert "build_province_id_grid" in res.json()["detail"]


@pytest.mark.parametrize(
    "route, filename",
    [
        ("province_id_runs", "province_id_runs.bin.gz"),
        ("province_id_grid_q4", "province_id_grid_q4.bin.gz"),
    ],
)
def test_public_artifact_routes_serve_bytes_verbatim(client, defines_dir, route, filename):
    target = defines_dir / "main" / filename
    target.parent.mkdir(parents=True)
    target.write_bytes(gzip.compress(b"geometry"))

    res = client.get(f"/main/data/{route}")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/gzip"
    assert gzip.decompress(res.content) == b"geometry"


@pytest.mark.parametrize("route", ["province_id_runs", "province_id_grid_q4"])
def test_public_artifact_routes_are_map_gated(client, defines_dir, route):
    assert client.get(f"/dev/data/{route}").status_code == 403


def test_index_is_revalidated_not_heuristically_cached(client):
    res = client.get("/main/chronicle/index")
    # A stale index silently hides newly captured days, so the browser must
    # re-check every time even though it may keep the body.
    assert "no-cache" in res.headers["cache-control"]
    assert res.headers["etag"]

    again = client.get(
        "/main/chronicle/index", headers={"If-None-Match": res.headers["etag"]}
    )
    assert again.status_code == 304


def test_geometry_version_is_memoized_per_artifact(client, chronicle_env, monkeypatch):
    from src.api import chronicle_routes

    artifact = chronicle_env / "defines" / "main" / "province_id_runs.bin.gz"
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(b"geometry")
    monkeypatch.setattr(
        chronicle_routes,
        "defines_file",
        lambda map_name, filename: str(chronicle_env / "defines" / map_name / filename),
    )

    hashed: list[str] = []
    monkeypatch.setattr(
        chronicle_routes,
        "geometry_version",
        lambda map_name: hashed.append(map_name) or "deadbeef",
    )
    chronicle_routes._geometry_version_cache.clear()

    first = client.get("/main/chronicle/index").json()["geometry_version"]
    second = client.get("/main/chronicle/index").json()["geometry_version"]

    assert first == second == "deadbeef"
    assert hashed == ["main"], "artifact unchanged, so it must be hashed once"

    # Rebuilding the artifact has to invalidate the memo.
    os.utime(artifact, (0, 0))
    client.get("/main/chronicle/index")
    assert len(hashed) == 2

    chronicle_routes._geometry_version_cache.clear()


def test_background_capture_swallows_and_logs_failures(chronicle_env, monkeypatch, caplog):
    from src.api import chronicle_routes

    def _explode(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr("src.scripts.chronicle.capture.capture_snapshot", _explode)

    with caplog.at_level("WARNING"):
        # Must not raise: this runs in a BackgroundTask after the 200 was sent.
        chronicle_routes._run_capture("main", "2026-01-01", False)

    assert "Chronicle capture failed" in caplog.text
    assert "2026-01-01" in caplog.text


# ---------------------------------------------------------------------------
# Regression: the access gate normalises the map id, downstream work must too
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("segment", ["%20main", "MaIn", "MAIN%20"])
def test_index_normalises_map_id_like_the_access_gate(client, segment):
    """ensure_map_access grants " main"/"MaIn" as "main", so the routes must
    query "main" as well.

    Before the fix the whitespace form raised ValueError("Invalid map name") out
    of validate_map into an uncaught 500 (anonymous, unauthenticated), and the
    case form returned a cheerful 200 with days: [] because it queried a map_id
    that does not exist.
    """
    _write_day("main", "2026-01-01", "nation", {"a": 1})

    res = client.get(f"/{segment}/chronicle/index")
    assert res.status_code == 200
    assert res.json()["days"] == ["2026-01-01"]


@pytest.mark.parametrize("segment", ["%20main", "MaIn"])
def test_data_route_normalises_map_id_like_the_access_gate(client, segment):
    _write_day("main", "2026-01-01", "nation", {"a": 1})

    res = client.get(f"/{segment}/chronicle/2026-01-01/data/nation")
    assert res.status_code == 200
    assert json.loads(gzip.decompress(res.content)) == {"a": 1}


def test_public_data_routes_normalise_map_id(client, defines_dir):
    target = defines_dir / "main" / "province_id_runs.bin.gz"
    target.parent.mkdir(parents=True)
    target.write_bytes(gzip.compress(b"geometry"))

    for segment in ("%20main", "MaIn"):
        res = client.get(f"/{segment}/data/province_id_runs")
        assert res.status_code == 200, segment
        assert gzip.decompress(res.content) == b"geometry"


# ---------------------------------------------------------------------------
# Regression: the snapshot trigger is registry-gated and time-bounded
# ---------------------------------------------------------------------------


def _localhost_client():
    return TestClient(app, client=("127.0.0.1", 12345))


def test_snapshot_post_rejects_unregistered_map(chronicle_env, monkeypatch):
    """require_localhost accepts the whole LAN, so it cannot be the only gate:
    an unregistered map would otherwise get a day directory and an index row."""
    calls: list[tuple] = []
    monkeypatch.setattr(
        "src.scripts.chronicle.capture.capture_snapshot",
        lambda *args, **kwargs: calls.append(args),
    )
    with _localhost_client() as test_client:
        res = test_client.post("/notamap/chronicle/snapshot")

    assert res.status_code == 404
    assert calls == []


def test_snapshot_post_normalises_the_map_id(chronicle_env, monkeypatch):
    calls: list[tuple] = []
    monkeypatch.setattr(
        "src.scripts.chronicle.capture.capture_snapshot",
        lambda *args, **kwargs: calls.append(args),
    )
    with _localhost_client() as test_client:
        res = test_client.post("/MaIn/chronicle/snapshot")

    assert res.status_code == 200
    assert res.json()["map"] == "main"
    assert calls == [("main", None, False)]


@pytest.mark.parametrize("day", ["9999-12-31", "0001-01-01", "2000-06-01"])
def test_snapshot_post_rejects_days_outside_the_backfill_window(
    chronicle_env, monkeypatch, day
):
    calls: list[tuple] = []
    monkeypatch.setattr(
        "src.scripts.chronicle.capture.capture_snapshot",
        lambda *args, **kwargs: calls.append(args),
    )
    with _localhost_client() as test_client:
        res = test_client.post(f"/main/chronicle/snapshot?day={day}")

    assert res.status_code == 400
    assert calls == []


def test_snapshot_post_accepts_a_recent_day(chronicle_env, monkeypatch):
    from datetime import datetime, timedelta, timezone

    day = (datetime.now(timezone.utc).date() - timedelta(days=2)).strftime("%Y-%m-%d")
    calls: list[tuple] = []
    monkeypatch.setattr(
        "src.scripts.chronicle.capture.capture_snapshot",
        lambda *args, **kwargs: calls.append(args),
    )
    with _localhost_client() as test_client:
        res = test_client.post(f"/main/chronicle/snapshot?day={day}")

    assert res.status_code == 200
    assert calls == [("main", day, False)]


# ---------------------------------------------------------------------------
# Regression: a vanished file is a 404, not a 500
# ---------------------------------------------------------------------------


def test_file_removed_between_resolve_and_stat_is_404(client, monkeypatch):
    _write_day("main", "2026-01-01", "nation", {"a": 1})
    path = store.stored_file_path("main", "2026-01-01", "nation")

    def _resolve_then_delete(*args, **kwargs):
        # Stand-in for a wipe or a temp-file replace landing between
        # resolve_stored_file's exists() and conditional_file_response's stat().
        os.remove(path)
        return path

    monkeypatch.setattr(
        "src.api.chronicle_routes.resolve_stored_file", _resolve_then_delete
    )

    res = client.get("/main/chronicle/2026-01-01/data/nation")
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# Regression: partial captures are visible in the index
# ---------------------------------------------------------------------------


def test_index_reports_days_with_missing_or_invalid_sources(client):
    _write_day("main", "2026-01-01", "nation", {"a": 1})
    store.upsert_snapshot(
        "main",
        "2026-01-02",
        "main",
        int(time.time()),
        0,
        None,
        {"files": {}, "missing": ["trade"], "invalid": ["nation"]},
    )

    body = client.get("/main/chronicle/index").json()
    # Additive fields only - the original shape is untouched.
    assert body["days"] == ["2026-01-01", "2026-01-02"]
    assert body["incomplete_day_count"] == 1
    assert body["incomplete_days"] == [
        {"day": "2026-01-02", "missing": ["trade"], "invalid": ["nation"]}
    ]


def test_index_reports_no_incomplete_days_for_a_clean_capture(client):
    _write_day("main", "2026-01-01", "nation", {"a": 1})

    body = client.get("/main/chronicle/index").json()
    assert body["incomplete_days"] == []
    assert body["incomplete_day_count"] == 0


# ---------------------------------------------------------------------------
# Regression: the chronicle must not capture a stale zoc_overlays.json
# ---------------------------------------------------------------------------


def test_marker_upload_regenerates_zoc_overlays_before_capturing(monkeypatch, tmp_path):
    """capture_if_due reads zoc_overlays.json off disk, so it has to run after
    generate_zoc_overlays or every stored day holds overlays that disagree with
    the markers captured beside them."""
    from src.api import data_routes

    order: list[str] = []
    monkeypatch.setattr(
        data_routes, "generate_zoc_overlays", lambda m: order.append("zoc")
    )
    monkeypatch.setattr(
        "src.scripts.chronicle.capture.capture_if_due",
        lambda m: order.append("capture"),
    )
    monkeypatch.setattr(
        data_routes, "input_file", lambda m, f: str(tmp_path / m / f)
    )
    monkeypatch.setattr(
        data_routes, "defines_file", lambda m, f: str(tmp_path / m / f)
    )

    with TestClient(app, client=("127.0.0.1", 12345)) as test_client:
        res = test_client.post("/main/data/upload/map_markers", json={"markers": []})

    assert res.status_code == 200
    assert order == ["zoc", "capture"]
