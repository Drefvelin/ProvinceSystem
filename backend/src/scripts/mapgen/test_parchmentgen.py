import os
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

from . import parchmentgen
from .parchmentgen import (
    PAPER_HIGH,
    PAPER_MID,
    PAPER_SHADOW,
    PREVIEW_FILENAME,
    PREVIEW_MAX_SIZE,
    _grade_parchment,
    _remap_luminance_value,
    create_map_preview,
    map_preview_path,
)


class ParchmentgenTests(unittest.TestCase):
    def test_remap_luminance_endpoints(self):
        self.assertEqual(_remap_luminance_value(0), PAPER_SHADOW)
        self.assertEqual(_remap_luminance_value(128), PAPER_MID)
        self.assertEqual(_remap_luminance_value(255), PAPER_HIGH)

    def test_grade_parchment_output_mode(self):
        bright_input = Image.new("RGB", (16, 16), (255, 255, 255))
        result = _grade_parchment(bright_input)
        self.assertEqual(result.mode, "RGBA")

        r, g, b, a = result.getpixel((8, 8))
        self.assertEqual(a, 255)
        self.assertGreater(r, 170)
        self.assertGreater(g, 160)
        self.assertGreaterEqual(r, g)

    def test_grade_removes_green_cast(self):
        green = Image.new("RGB", (8, 8), (0, 200, 0))
        result = _grade_parchment(green)
        r, g, b, _ = result.getpixel((4, 4))
        self.assertLessEqual(g, max(r, b) + 5)

    def test_remap_luminance_monotonic_lightness(self):
        low = _remap_luminance_value(32)
        high = _remap_luminance_value(224)
        self.assertLess(sum(low), sum(high))


class MapPreviewTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = self._tmp.name

        def input_file(map_name, filename):
            path = os.path.join(self.root, "input", map_name, filename)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            return path

        def parchment_image(map_name):
            path = os.path.join(self.root, "output", map_name, "maps", "parchment_base.png")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            return path

        for name, value in (
            ("input_file", input_file),
            ("parchment_image", parchment_image),
        ):
            patcher = patch.object(parchmentgen, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

        self.input_file = input_file
        self.parchment_image = parchment_image

    def test_preview_sits_next_to_the_generated_map_images(self):
        path = map_preview_path("testmap")
        self.assertEqual(os.path.basename(path), PREVIEW_FILENAME)
        self.assertEqual(
            os.path.dirname(path), os.path.dirname(self.parchment_image("testmap"))
        )

    def test_creates_downscaled_webp(self):
        source = self.input_file("testmap", "map.png")
        Image.new("RGB", (3200, 3200), (90, 120, 60)).save(source)

        out = create_map_preview("testmap")
        self.assertTrue(os.path.exists(out))

        with Image.open(out) as preview:
            self.assertEqual(preview.format, "WEBP")
            self.assertEqual(max(preview.size), PREVIEW_MAX_SIZE)
        self.assertLess(os.path.getsize(out), os.path.getsize(source))

    def test_non_square_map_keeps_aspect_ratio(self):
        Image.new("RGB", (1600, 800), (10, 20, 30)).save(
            self.input_file("testmap", "map.png")
        )
        with Image.open(create_map_preview("testmap")) as preview:
            self.assertEqual(preview.size, (PREVIEW_MAX_SIZE, PREVIEW_MAX_SIZE // 2))

    def test_missing_map_png_returns_none(self):
        self.assertIsNone(create_map_preview("testmap"))


if __name__ == "__main__":
    unittest.main()
