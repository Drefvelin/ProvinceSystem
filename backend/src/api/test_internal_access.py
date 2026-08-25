"""Unit tests for internal localhost access helper."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_SRC = _BACKEND_ROOT / "src"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

from fastapi import HTTPException

from src.api.internal_access import require_localhost


def _request_with_host(host: str | None) -> MagicMock:
    request = MagicMock()
    if host is None:
        request.client = None
    else:
        request.client = MagicMock(host=host)
    return request


class InternalAccessTest(unittest.TestCase):
    def test_accepts_ipv4_loopback(self) -> None:
        require_localhost(_request_with_host("127.0.0.1"))

    def test_accepts_ipv6_loopback(self) -> None:
        require_localhost(_request_with_host("::1"))

    def test_rejects_remote_ip(self) -> None:
        with self.assertRaises(HTTPException) as ctx:
            require_localhost(_request_with_host("203.0.113.1"))
        self.assertEqual(403, ctx.exception.status_code)
        self.assertIn("localhost", ctx.exception.detail.lower())

    def test_rejects_missing_client(self) -> None:
        with self.assertRaises(HTTPException) as ctx:
            require_localhost(_request_with_host(None))
        self.assertEqual(403, ctx.exception.status_code)


if __name__ == "__main__":
    unittest.main()
