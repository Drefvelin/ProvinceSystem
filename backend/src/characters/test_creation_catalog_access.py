"""Tests for web_creator_access catalog persistence and create gate."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_BACKEND_SRC = Path(__file__).resolve().parents[1]
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))
_BACKEND = Path(__file__).resolve().parents[2]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

MINIMAL_CATALOG = {
    "stages": [{"id": "info", "type": "info", "order": 0}],
    "attribute_point_buy": {
        "pool": 12,
        "max_rank": 2,
        "cost_for_rank": [1, 2],
        "attributes": ["strength", "dexterity", "constitution"],
        "abbreviations": {
            "strength": "str",
            "dexterity": "dex",
            "constitution": "con",
        },
    },
    "races": [{"id": "human", "name": "Human"}],
    "traits": [],
    "classes": [{"id": "warrior", "name": "Warrior"}],
    "validation": {"name_max": 24, "age_min": 16},
    "slot_limits": {"hard_cap": 10, "default": 1},
}


class CreationCatalogAccessTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.db_path = root / "province.db"

        import skins.db as db_mod

        self._db_mod = db_mod
        sys.modules["src.skins.db"] = db_mod
        self._orig_db = db_mod.DB_PATH
        self._orig_data = db_mod.DATA_DIR
        self._orig_skins = db_mod.SKINS_DIR
        self._orig_drinks = db_mod.DRINKS_DIR
        self._orig_wardrobe = db_mod.WARDROBE_DIR
        db_mod.DATA_DIR = root
        db_mod.DB_PATH = self.db_path
        db_mod.SKINS_DIR = root / "skins"
        db_mod.DRINKS_DIR = root / "drinks"
        db_mod.WARDROBE_DIR = root / "wardrobe"
        db_mod.migrate()

    def tearDown(self) -> None:
        db_mod = self._db_mod
        db_mod.DB_PATH = self._orig_db
        db_mod.DATA_DIR = self._orig_data
        db_mod.SKINS_DIR = self._orig_skins
        db_mod.DRINKS_DIR = self._orig_drinks
        db_mod.WARDROBE_DIR = self._orig_wardrobe
        self.tmp.cleanup()

    def test_kebab_case_normalizes_to_snake_case(self) -> None:
        from characters.creation_catalog import _normalize_web_creator_access

        out = _normalize_web_creator_access(
            {
                "by-realm": {
                    "main": {"min-tier": 1, "min-group-id": "noble"},
                    "dev": {"min-tier": 0},
                }
            }
        )
        self.assertEqual(
            out,
            {
                "by_realm": {
                    "main": {"min_tier": 1, "min_group_id": "noble"},
                    "dev": {"min_tier": 0},
                }
            },
        )

    def test_replace_and_get_catalog_round_trip(self) -> None:
        from characters.creation_catalog import get_catalog, replace_catalog
        from characters.web_creator_access import resolve_gate
        from skins.db import connect

        payload = {
            **MINIMAL_CATALOG,
            "web_creator_access": {
                "by_realm": {
                    "main": {"min_tier": 1, "min_group_id": "noble"},
                    "tutorial": {"min_tier": 0},
                }
            },
        }
        replace_catalog(payload)
        stored = get_catalog()
        self.assertEqual(
            stored["web_creator_access"],
            payload["web_creator_access"],
        )

        with connect() as conn:
            row = conn.execute(
                "SELECT payload FROM creation_catalog WHERE id = 1"
            ).fetchone()
        data = json.loads(row["payload"])
        self.assertIn("web_creator_access", data)
        self.assertEqual(data["web_creator_access"]["by_realm"]["main"]["min_tier"], 1)

        gate = resolve_gate(
            stored,
            realm_id="main",
            entitlements={"donator_tier": 0},
        )
        self.assertFalse(gate["web_creator_allowed"])

    def test_create_character_blocked_when_tier_below_policy(self) -> None:
        from characters import creates as creates_mod
        from characters.creation_catalog import replace_catalog

        replace_catalog(
            {
                **MINIMAL_CATALOG,
                "web_creator_access": {
                    "by_realm": {"main": {"min_tier": 1, "min_group_id": "noble"}}
                },
            }
        )

        with mock.patch.object(
            creates_mod,
            "_validate_and_normalize",
            return_value={"client_request_id": None, "name": "Blocked"},
        ), mock.patch(
            "src.characters.rpc_player_meta.resolve_web_entitlements",
            return_value={
                "donator_tier": 0,
                "name_colour_stops": 0,
                "wardrobe_skin_slots": 1,
                "max_alive_characters": 3,
                "meta_synced": True,
                "permission_flags": {},
            },
        ):
            with self.assertRaises(creates_mod.CreateError) as ctx:
                creates_mod.create_character(
                    "player-gate-1",
                    {"name": "Blocked"},
                    realm_id="main",
                )
        self.assertIn("noble", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
