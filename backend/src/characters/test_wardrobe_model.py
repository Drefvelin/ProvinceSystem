"""Unit tests for wardrobe arm model override."""

from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[2]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from PIL import Image  # noqa: E402

from src.characters.wardrobe import (  # noqa: E402
    detect_skin_model,
    resolve_skin_model,
)


def _classic_png() -> bytes:
    img = Image.new("RGBA", (64, 64), (40, 40, 40, 255))
    img.putpixel((54, 20), (10, 10, 10, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _slim_png() -> bytes:
    img = Image.new("RGBA", (64, 64), (40, 40, 40, 255))
    img.putpixel((54, 20), (0, 0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class ResolveSkinModelTests(unittest.TestCase):
    def test_detect_classic_and_slim(self) -> None:
        self.assertEqual(detect_skin_model(_classic_png()), "classic")
        self.assertEqual(detect_skin_model(_slim_png()), "slim")

    def test_override_slim_on_classic_png(self) -> None:
        png = _classic_png()
        self.assertEqual(detect_skin_model(png), "classic")
        self.assertEqual(resolve_skin_model(png, "slim"), "slim")

    def test_override_classic_on_slim_png(self) -> None:
        png = _slim_png()
        self.assertEqual(detect_skin_model(png), "slim")
        self.assertEqual(resolve_skin_model(png, "classic"), "classic")
        self.assertEqual(resolve_skin_model(png, "wide"), "classic")

    def test_empty_override_falls_back_to_detect(self) -> None:
        png = _slim_png()
        self.assertEqual(resolve_skin_model(png, None), "slim")
        self.assertEqual(resolve_skin_model(png, ""), "slim")


if __name__ == "__main__":
    unittest.main()
