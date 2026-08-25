"""Route handler tests for localhost-gated internal map routes."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_SRC = _BACKEND_ROOT / "src"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

from fastapi import BackgroundTasks, HTTPException

from src.scripts.util.auth import HASHED_KEY


def _request_with_host(host: str) -> MagicMock:
    request = MagicMock()
    request.client = MagicMock(host=host)
    return request


class InternalRoutesTest(unittest.IsolatedAsyncioTestCase):
    async def test_upload_queue_rejects_remote(self) -> None:
        from src.api.claim_routes import upload_queue

        request = _request_with_host("203.0.113.1")
        with self.assertRaises(HTTPException) as ctx:
            await upload_queue("main", "wrong-hash-on-purpose", request)
        self.assertEqual(403, ctx.exception.status_code)

    async def test_regenerate_rejects_remote(self) -> None:
        from src.api.regen_routes import regenerate_map

        request = _request_with_host("8.8.8.8")
        with self.assertRaises(HTTPException) as ctx:
            await regenerate_map(
                "main",
                HASHED_KEY,
                "fullregen",
                BackgroundTasks(),
                request,
            )
        self.assertEqual(403, ctx.exception.status_code)

    async def test_upload_queue_allows_localhost(self) -> None:
        from src.api.claim_routes import upload_queue

        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            queue_path = os.path.join(tmp, "queue.json")

            request = _request_with_host("127.0.0.1")
            request.json = AsyncMock(return_value={"survival": []})

            with patch("src.api.claim_routes.raw_queue_path", return_value=queue_path):
                response = await upload_queue("main", HASHED_KEY, request)

            self.assertEqual(200, response.status_code)
            body = json.loads(response.body)
            self.assertTrue(body["success"])
            self.assertEqual("main", body["map"])
            self.assertTrue(os.path.isfile(queue_path))

    async def test_regenerate_allows_localhost(self) -> None:
        from src.api.regen_routes import regenerate_map

        request = _request_with_host("127.0.0.1")
        tasks = BackgroundTasks()

        with patch("src.api.regen_routes.validate_map"), patch(
            "src.api.regen_routes.run_regeneration"
        ):
            response = await regenerate_map(
                "main",
                HASHED_KEY,
                "fullregen",
                tasks,
                request,
            )

        self.assertEqual(200, response.status_code)
        body = json.loads(response.body)
        self.assertTrue(body["success"])
        self.assertEqual("main", body["map"])
        self.assertEqual("fullregen", body["regen_type"])


if __name__ == "__main__":
    unittest.main()
