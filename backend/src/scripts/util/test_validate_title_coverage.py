"""Tests for validate_title_coverage."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.scripts.util.validate_title_coverage import validate_title_coverage


class TestValidateTitleCoverage(unittest.TestCase):
    def test_counties_only_happy_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            defines = Path(tmp) / "defines" / "fixture"
            defines.mkdir(parents=True)

            (defines / "provinces.txt").write_text(
                "1=10,20,30;plains;5\n2=20,30,40;hills;3\n",
                encoding="utf-8",
            )
            (defines / "county.json").write_text(
                json.dumps(
                    {
                        "COUNTY_A": {"name": "A", "rgb": "1,2,3", "provinces": [1]},
                        "COUNTY_B": {"name": "B", "rgb": "4,5,6", "provinces": [2]},
                    }
                ),
                encoding="utf-8",
            )
            (defines / "duchy.json").write_text("{}", encoding="utf-8")

            with patch(
                "src.scripts.util.validate_title_coverage.defines_file",
                lambda map_name, filename: str(defines / filename),
            ):
                with patch(
                    "src.scripts.loader.provinces.defines_file",
                    lambda map_name, filename: str(defines / filename),
                ):
                    with patch(
                        "src.scripts.util.validate_title_coverage.validate_map",
                        lambda map_name: None,
                    ):
                        with patch(
                            "src.scripts.loader.provinces.validate_map",
                            lambda map_name: None,
                        ):
                            errors = validate_title_coverage("fixture")

            self.assertEqual(errors, [])

    def test_duplicate_province_in_counties(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            defines = Path(tmp) / "defines" / "fixture"
            defines.mkdir(parents=True)

            (defines / "provinces.txt").write_text("1=10,20,30\n", encoding="utf-8")
            (defines / "county.json").write_text(
                json.dumps(
                    {
                        "A": {"name": "A", "rgb": "1,2,3", "provinces": [1]},
                        "B": {"name": "B", "rgb": "4,5,6", "provinces": [1]},
                    }
                ),
                encoding="utf-8",
            )
            (defines / "duchy.json").write_text("{}", encoding="utf-8")

            with patch(
                "src.scripts.util.validate_title_coverage.defines_file",
                lambda map_name, filename: str(defines / filename),
            ):
                with patch(
                    "src.scripts.loader.provinces.defines_file",
                    lambda map_name, filename: str(defines / filename),
                ):
                    with patch(
                        "src.scripts.util.validate_title_coverage.validate_map",
                        lambda map_name: None,
                    ):
                        with patch(
                            "src.scripts.loader.provinces.validate_map",
                            lambda map_name: None,
                        ):
                            errors = validate_title_coverage("fixture")

            self.assertTrue(
                any("Province 1 is assigned to both" in e for e in errors)
            )

    def test_county_in_two_duchies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            defines = Path(tmp) / "defines" / "fixture"
            defines.mkdir(parents=True)

            (defines / "provinces.txt").write_text("1=10,20,30\n", encoding="utf-8")
            (defines / "county.json").write_text(
                json.dumps(
                    {"COUNTY_1": {"name": "C1", "rgb": "1,2,3", "provinces": [1]}}
                ),
                encoding="utf-8",
            )
            (defines / "duchy.json").write_text(
                json.dumps(
                    {
                        "DUCHY_A": {
                            "name": "A",
                            "rgb": "10,20,30",
                            "titles": ["COUNTY_1"],
                        },
                        "DUCHY_B": {
                            "name": "B",
                            "rgb": "40,50,60",
                            "titles": ["COUNTY_1"],
                        },
                    }
                ),
                encoding="utf-8",
            )

            with patch(
                "src.scripts.util.validate_title_coverage.defines_file",
                lambda map_name, filename: str(defines / filename),
            ):
                with patch(
                    "src.scripts.loader.provinces.defines_file",
                    lambda map_name, filename: str(defines / filename),
                ):
                    with patch(
                        "src.scripts.util.validate_title_coverage.validate_map",
                        lambda map_name: None,
                    ):
                        with patch(
                            "src.scripts.loader.provinces.validate_map",
                            lambda map_name: None,
                        ):
                            errors = validate_title_coverage("fixture")

            self.assertTrue(
                any(
                    "COUNTY_1' is assigned to both 'DUCHY_A' and 'DUCHY_B'"
                    in e
                    for e in errors
                )
            )


if __name__ == "__main__":
    unittest.main()
