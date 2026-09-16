"""Title and regions payload validation without importing the FastAPI app."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_SRC = _BACKEND_ROOT / "src"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

from api.editor_validation import RegionsValidationError, validate_regions_payload


class RegionsValidationTest(unittest.TestCase):
    def test_empty_object_is_valid(self) -> None:
        self.assertEqual(validate_regions_payload({}), {})

    def test_sanitizes_name_and_provinces(self) -> None:
        clean = validate_regions_payload(
            {
                "REGION_1": {
                    "name": " Highlands ",
                    "provinces": [3, "7"],
                    "rgb": "10,20,30",
                }
            }
        )
        self.assertEqual(clean["REGION_1"]["name"], "Highlands")
        self.assertEqual(clean["REGION_1"]["provinces"], [3, 7])
        self.assertEqual(clean["REGION_1"]["rgb"], "10,20,30")

    def test_duplicate_province_rejected(self) -> None:
        with self.assertRaises(RegionsValidationError) as ctx:
            validate_regions_payload(
                {
                    "REGION_1": {"provinces": [1]},
                    "REGION_2": {"provinces": [1]},
                }
            )
        self.assertIn("Province 1", str(ctx.exception))

    def test_non_object_entry_rejected(self) -> None:
        with self.assertRaises(RegionsValidationError):
            validate_regions_payload({"REGION_1": [1, 2]})

    def test_non_object_payload_rejected(self) -> None:
        with self.assertRaises(RegionsValidationError):
            validate_regions_payload([])  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
