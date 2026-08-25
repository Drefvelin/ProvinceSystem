"""Unit tests for production startup guard."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_SRC = _BACKEND_ROOT / "src"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

from src.api.prod_guard import assert_production_safe


class ProdGuardTest(unittest.TestCase):
    def test_non_prod_allows_skins_dev(self) -> None:
        with patch.dict(os.environ, {"SKINS_DEV": "1"}, clear=True):
            assert_production_safe()

    def test_prod_rejects_skins_dev(self) -> None:
        env = {
            "PS_PRODUCTION": "1",
            "SKINS_DEV": "1",
            "PLUGIN_KEY": "real-plugin",
            "STAFF_KEY": "real-staff",
        }
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(RuntimeError) as ctx:
                assert_production_safe()
        self.assertIn("SKINS_DEV", str(ctx.exception))

    def test_prod_rejects_character_ui_dev(self) -> None:
        env = {
            "PS_PRODUCTION": "1",
            "CHARACTER_UI_DEV": "1",
            "PLUGIN_KEY": "real-plugin",
            "STAFF_KEY": "real-staff",
        }
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(RuntimeError) as ctx:
                assert_production_safe()
        self.assertIn("CHARACTER_UI_DEV", str(ctx.exception))

    def test_prod_rejects_missing_plugin_key(self) -> None:
        env = {
            "PS_PRODUCTION": "1",
            "STAFF_KEY": "real-staff",
        }
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(RuntimeError) as ctx:
                assert_production_safe()
        self.assertIn("PLUGIN_KEY", str(ctx.exception))

    def test_prod_rejects_missing_staff_key(self) -> None:
        env = {
            "PS_PRODUCTION": "1",
            "PLUGIN_KEY": "real-plugin",
        }
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(RuntimeError) as ctx:
                assert_production_safe()
        self.assertIn("STAFF_KEY", str(ctx.exception))

    def test_prod_accepts_valid_env(self) -> None:
        env = {
            "PS_PRODUCTION": "1",
            "PLUGIN_KEY": "real-plugin",
            "STAFF_KEY": "real-staff",
        }
        with patch.dict(os.environ, env, clear=True):
            assert_production_safe()


if __name__ == "__main__":
    unittest.main()
