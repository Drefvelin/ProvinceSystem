"""Route tests for the precedent API (DB/embedding/synthesis calls fully mocked)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_SRC = _BACKEND_ROOT / "src"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

import os

os.environ.setdefault("SKINS_DEV", "1")

from fastapi.testclient import TestClient  # noqa: E402

from server import app  # noqa: E402
import src.api.precedent_routes as routes  # noqa: E402

_HEADERS = {"X-Staff-Key": "dev-staff-key"}


class PrecedentRoutesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        routes._SEARCH_RATE_BUCKETS.clear()
        patcher = mock.patch("src.api.precedent_routes.migrate")
        self.addCleanup(patcher.stop)
        patcher.start()

    def tearDown(self) -> None:
        self.client.close()
        routes._SEARCH_RATE_BUCKETS.clear()

    # --- auth ---

    def test_log_case_no_auth(self) -> None:
        res = self.client.post("/precedent/staff/log", json={"logged_by": "x", "summary": "s"})
        self.assertEqual(res.status_code, 401)

    def test_search_no_auth(self) -> None:
        res = self.client.post("/precedent/staff/search", json={"query": "q"})
        self.assertEqual(res.status_code, 401)

    def test_get_case_no_auth(self) -> None:
        res = self.client.get("/precedent/staff/case/abc")
        self.assertEqual(res.status_code, 401)

    def test_delete_case_no_auth(self) -> None:
        res = self.client.delete("/precedent/staff/case/abc")
        self.assertEqual(res.status_code, 401)

    def test_ping_no_auth(self) -> None:
        res = self.client.get("/precedent/staff/ping")
        self.assertEqual(res.status_code, 401)

    # --- log case ---

    @mock.patch("src.api.precedent_routes.insert_case", return_value="new-id")
    @mock.patch("src.api.precedent_routes.embed", return_value=[0.1])
    def test_log_case_success(self, mock_embed, mock_insert) -> None:
        res = self.client.post(
            "/precedent/staff/log",
            json={"logged_by": "Staffer", "summary": "s"},
            headers=_HEADERS,
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"id": "new-id"})

    def test_log_case_rejects_oversized_summary(self) -> None:
        res = self.client.post(
            "/precedent/staff/log",
            json={"logged_by": "Staffer", "summary": "x" * 1001},
            headers=_HEADERS,
        )
        self.assertEqual(res.status_code, 422)

    def test_log_case_rejects_oversized_player(self) -> None:
        res = self.client.post(
            "/precedent/staff/log",
            json={"logged_by": "Staffer", "summary": "s", "players": ["x" * 201]},
            headers=_HEADERS,
        )
        self.assertEqual(res.status_code, 422)

    # --- search ---

    @mock.patch("src.api.precedent_routes.synthesize", return_value="synthesis text")
    @mock.patch("src.api.precedent_routes.search_similar", return_value=[])
    @mock.patch("src.api.precedent_routes.embed", return_value=[0.1])
    def test_search_returns_max_distance(self, mock_embed, mock_search, mock_synth) -> None:
        res = self.client.post(
            "/precedent/staff/search", json={"query": "q"}, headers=_HEADERS
        )
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertEqual(body["max_distance"], routes.MAX_RELEVANT_DISTANCE)

    @mock.patch("src.api.precedent_routes.synthesize", return_value="synthesis text")
    @mock.patch("src.api.precedent_routes.search_similar", return_value=[])
    @mock.patch("src.api.precedent_routes.embed", return_value=[0.1])
    def test_search_forwards_players(self, mock_embed, mock_search, mock_synth) -> None:
        res = self.client.post(
            "/precedent/staff/search",
            json={"query": "q", "players": ["Alice"]},
            headers=_HEADERS,
        )
        self.assertEqual(res.status_code, 200)
        _, kwargs = mock_search.call_args
        self.assertEqual(kwargs.get("players"), ["Alice"])

    @mock.patch("src.api.precedent_routes.synthesize", return_value="synthesis text")
    @mock.patch("src.api.precedent_routes.search_similar", return_value=[])
    @mock.patch("src.api.precedent_routes.embed", return_value=[0.1])
    def test_search_rate_limited(self, mock_embed, mock_search, mock_synth) -> None:
        for _ in range(routes._SEARCH_RATE_LIMIT):
            res = self.client.post(
                "/precedent/staff/search", json={"query": "q"}, headers=_HEADERS
            )
            self.assertEqual(res.status_code, 200)
        res = self.client.post(
            "/precedent/staff/search", json={"query": "q"}, headers=_HEADERS
        )
        self.assertEqual(res.status_code, 429)

    # --- get case ---

    @mock.patch("src.api.precedent_routes.get_case", return_value=None)
    def test_get_case_not_found(self, mock_get) -> None:
        res = self.client.get("/precedent/staff/case/missing", headers=_HEADERS)
        self.assertEqual(res.status_code, 404)

    @mock.patch(
        "src.api.precedent_routes.get_case",
        return_value={
            "id": "1",
            "logged_by": "x",
            "players": [],
            "summary": "s",
            "rule": "",
            "ruling": "",
            "punishment": "",
            "created_at": None,
        },
    )
    def test_get_case_success(self, mock_get) -> None:
        res = self.client.get("/precedent/staff/case/1", headers=_HEADERS)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["id"], "1")

    # --- delete case ---

    @mock.patch("src.api.precedent_routes.delete_case", return_value=False)
    def test_delete_case_not_found(self, mock_delete) -> None:
        res = self.client.delete("/precedent/staff/case/missing", headers=_HEADERS)
        self.assertEqual(res.status_code, 404)

    @mock.patch("src.api.precedent_routes.delete_case", return_value=True)
    def test_delete_case_success(self, mock_delete) -> None:
        res = self.client.delete("/precedent/staff/case/1", headers=_HEADERS)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"deleted": True, "id": "1"})

    # --- ping ---

    @mock.patch("src.api.precedent_routes.ping_db")
    def test_ping_success(self, mock_ping) -> None:
        res = self.client.get("/precedent/staff/ping", headers=_HEADERS)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"ok": True})


if __name__ == "__main__":
    unittest.main()
