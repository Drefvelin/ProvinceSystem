"""Sanity check: banner pattern catalog matches PNG assets in input/dev/banner."""

import unittest

from src.scripts.bannergen.patterns_catalog import (
    ALL_PATTERNS,
    TFMC_PATTERNS,
    VANILLA_PATTERNS,
    catalog_png_mismatches,
    png_pattern_names,
)


class TestPatternsCatalog(unittest.TestCase):
    def test_vanilla_and_tfmc_disjoint(self):
        overlap = VANILLA_PATTERNS & TFMC_PATTERNS
        self.assertEqual(len(overlap), 0, f"overlap: {overlap}")

    def test_all_patterns_union(self):
        self.assertEqual(ALL_PATTERNS, VANILLA_PATTERNS | TFMC_PATTERNS)

    def test_dev_banner_pngs_match_catalog(self):
        missing, orphan = catalog_png_mismatches("dev")
        self.assertEqual(missing, [], f"missing PNGs for catalog patterns: {missing}")
        self.assertEqual(orphan, [], f"orphan PNGs not in catalog: {orphan}")

    def test_main_banner_pngs_match_catalog(self):
        missing, orphan = catalog_png_mismatches("main")
        self.assertEqual(missing, [], f"missing PNGs for catalog patterns: {missing}")
        self.assertEqual(orphan, [], f"orphan PNGs not in catalog: {orphan}")

    def test_ribs_border_present(self):
        pngs = png_pattern_names("dev")
        self.assertIn("RIBS_BORDER", pngs)
        self.assertIn("RIBS_BORDER", TFMC_PATTERNS)
        self.assertIn("CROWNS", TFMC_PATTERNS)


if __name__ == "__main__":
    unittest.main()
