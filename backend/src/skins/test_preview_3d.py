"""Tests for 3D review-sheet tile selection (renderer mocked off)."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

_BACKEND_SRC = Path(__file__).resolve().parents[1]
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))


def _tiny_png() -> bytes:
    from io import BytesIO

    from PIL import Image

    buf = BytesIO()
    Image.new("RGBA", (16, 16), (40, 180, 80, 255)).save(buf, format="PNG")
    return buf.getvalue()


class Preview3dJobTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name)
        os.environ["SHEET_RENDER_DISABLE"] = "1"

    def tearDown(self) -> None:
        os.environ.pop("SHEET_RENDER_DISABLE", None)
        self.tmp.cleanup()

    def test_gun_job_lists_carry_aim_reload(self) -> None:
        from skins.preview_3d import _job_for_kind

        slug = "gun1"
        (self.out / f"{slug}.png").write_bytes(_tiny_png())
        for stem in ("carry", "aim", "reload"):
            (self.out / f"{slug}_{stem}.json").write_text("{}", encoding="utf-8")
        job = _job_for_kind("gun", slug, self.out, [])
        self.assertIsNotNone(job)
        self.assertEqual(job["views"], ["model", "carry", "reload", "aim"])

    def test_ensure_preview_skips_when_disabled(self) -> None:
        from skins.preview_3d import ensure_preview_tiles

        slug = "item1"
        (self.out / f"{slug}.png").write_bytes(_tiny_png())
        tiles = ensure_preview_tiles("handheld", slug, self.out)
        self.assertEqual(tiles, [])

    def test_editable_kit_keeps_skin_png_signed(self) -> None:
        from characters.creation_catalog import _normalize_editable_kit

        rows = _normalize_editable_kit(
            [
                {
                    "kit_key": "writable_book",
                    "path": "v.WRITABLE_BOOK",
                    "amount": 1,
                    "skin_png": "journal_skin",
                    "skin_png_signed": "journal_skin_signed",
                    "base_set": "books",
                    "2d_template": "book",
                }
            ]
        )
        self.assertEqual(rows[0]["skin_png_signed"], "journal_skin_signed")
        self.assertEqual(rows[0]["skin_png"], "journal_skin")

    def test_review_sheet_composites_existing_preview_tiles(self) -> None:
        from PIL import Image

        from skins.review_sheet import _preview_tiles_row

        path = self.out / "preview_model.png"
        Image.new("RGB", (64, 64), (10, 20, 30)).save(path)
        row = _preview_tiles_row([("model", path)])
        self.assertIsNotNone(row)
        self.assertGreaterEqual(row.width, 64)
        self.assertGreaterEqual(row.height, 64)


if __name__ == "__main__":
    unittest.main()
