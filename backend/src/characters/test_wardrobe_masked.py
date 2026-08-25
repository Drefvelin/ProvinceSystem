"""Unit tests for wardrobe masked compose + sequential stack helpers."""

from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path
from unittest import mock

_BACKEND = Path(__file__).resolve().parents[2]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from PIL import Image  # noqa: E402

from src.characters.wardrobe import (  # noqa: E402
    WardrobeError,
    compose_masked_skin,
    _require_sequential_fill,
)


def _png(color: tuple[int, int, int, int], *, head=None) -> bytes:
    img = Image.new("RGBA", (64, 64), color)
    if head is not None:
        for y in range(16):
            for x in range(64):
                img.putpixel((x, y), head)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class ComposeMaskedTest(unittest.TestCase):
    def test_head_from_base_body_from_template(self) -> None:
        base = _png((10, 20, 30, 255), head=(1, 2, 3, 255))
        templ = _png((200, 100, 50, 255), head=(0, 0, 0, 0))
        out = compose_masked_skin(base, templ)
        img = Image.open(io.BytesIO(out)).convert("RGBA")
        self.assertEqual(img.getpixel((8, 8))[:3], (1, 2, 3))
        self.assertEqual(img.getpixel((40, 8))[:3], (1, 2, 3))  # hat strip
        self.assertEqual(img.getpixel((20, 40))[:3], (200, 100, 50))


class SequentialFillTest(unittest.TestCase):
    def test_extra1_needs_base(self) -> None:
        with self.assertRaises(WardrobeError) as ctx:
            _require_sequential_fill("extra_1", {})
        self.assertIn("Base", str(ctx.exception))

    def test_extra2_needs_extra1(self) -> None:
        slots = {"base": {"png_relpath": "x"}}
        with self.assertRaises(WardrobeError) as ctx:
            _require_sequential_fill("extra_2", slots)
        self.assertIn("Skin 2", str(ctx.exception))

    def test_ok_when_prior_filled(self) -> None:
        slots = {
            "base": {"png_relpath": "a"},
            "extra_1": {"png_relpath": "b"},
        }
        _require_sequential_fill("extra_2", slots)


if __name__ == "__main__":
    unittest.main()
