"""Tests for pending create sheet enrichment."""

from __future__ import annotations

import unittest

from src.characters.pending_sheet import (
    build_attribute_totals,
    build_experience_modifiers,
    build_sheet_traits,
    enrich_pending_list_item,
    resolve_display_names,
)


CATALOG = {
    "stages": [
        {
            "id": "personality_selection_stage",
            "type": "selection",
            "target": "trait",
            "key": "personality",
        },
        {
            "id": "evil_selection_stage",
            "type": "selection",
            "target": "trait",
            "key": "evil",
        },
    ],
    "attribute_point_buy": {
        "attributes": ["strength", "dexterity"],
        "abbreviations": {"strength": "str", "dexterity": "dex"},
        "trait_id_pattern": "{abbr}{rank}",
    },
    "races": [
        {
            "id": "human",
            "name": "Human",
            "attribute_modifiers": [{"type": "charisma", "amount": 1}],
            "experience_modifiers": [
                {"profession": "farming", "alias": "Farming", "amount": 5}
            ],
        }
    ],
    "classes": [
        {
            "id": "warrior",
            "name": "Warrior",
            "attribute_modifiers": [{"type": "strength", "amount": 1}],
        }
    ],
    "traits": [
        {
            "id": "str1",
            "key": "attributes",
            "attribute_modifiers": [{"type": "strength", "amount": 1}],
        },
        {
            "id": "str2",
            "key": "attributes",
            "attribute_modifiers": [{"type": "strength", "amount": 1}],
        },
        {
            "id": "callous",
            "name": "Callous",
            "key": "personality",
            "attribute_modifiers": [
                {"type": "charisma", "amount": -1},
                {"type": "constitution", "amount": 1},
            ],
            "experience_modifiers": [
                {"profession": "combat", "alias": "Combat", "amount": 3}
            ],
        },
        {
            "id": "evil_tyrant",
            "name": "Tyrant",
            "key": "evil",
            "attribute_modifiers": [{"type": "strength", "amount": 1}],
        },
        {
            "id": "phys_strong",
            "name": "Strong",
            "key": "physical",
            "attribute_modifiers": [{"type": "strength", "amount": 2}],
        },
    ],
}

PAYLOAD = {
    "race_id": "human",
    "class_id": "warrior",
    "attributes": {"strength": 2, "dexterity": 0},
    "attribute_traits": ["str1", "str2"],
    "traits": ["callous", "evil_tyrant", "phys_strong"],
}


class PendingSheetTests(unittest.TestCase):
    def test_attribute_totals_sum_race_class_traits_not_ranks(self) -> None:
        totals = build_attribute_totals(PAYLOAD, CATALOG)
        # human +1 cha, warrior +1 str, str1+str2 +2 str, tyrant +1 str, phys_strong +2 str
        self.assertEqual(totals.get("strength"), 6)
        self.assertEqual(totals.get("charisma"), 0)
        self.assertEqual(totals.get("constitution"), 1)
        self.assertNotEqual(totals.get("strength"), 2)

    def test_experience_modifiers_merged(self) -> None:
        xp = build_experience_modifiers(PAYLOAD, CATALOG)
        by_prof = {row["profession"]: row for row in xp}
        self.assertEqual(by_prof["farming"]["amount"], 5)
        self.assertEqual(by_prof["combat"]["amount"], 3)

    def test_sheet_traits_use_selection_keys_only(self) -> None:
        traits = build_sheet_traits(PAYLOAD, CATALOG)
        keys = {t["key"] for t in traits}
        ids = {t["id"] for t in traits}
        self.assertIn("personality", keys)
        self.assertIn("evil", keys)
        self.assertNotIn("physical", keys)
        self.assertNotIn("str1", ids)
        callous = next(t for t in traits if t["id"] == "callous")
        self.assertEqual(callous["name"], "Callous")

    def test_resolve_display_names(self) -> None:
        race_name, class_name = resolve_display_names(PAYLOAD, CATALOG)
        self.assertEqual(race_name, "Human")
        self.assertEqual(class_name, "Warrior")

    def test_enrich_pending_list_item_shape(self) -> None:
        overlay = enrich_pending_list_item(PAYLOAD, CATALOG)
        self.assertIn("attributes", overlay)
        self.assertIn("traits", overlay)
        self.assertIn("experience_modifiers", overlay)
        self.assertEqual(overlay["race_name"], "Human")
        self.assertEqual(overlay["class_name"], "Warrior")


if __name__ == "__main__":
    unittest.main()
