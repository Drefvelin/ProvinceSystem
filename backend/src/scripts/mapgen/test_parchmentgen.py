import unittest

from PIL import Image

from .parchmentgen import (
    PAPER_HIGH,
    PAPER_MID,
    PAPER_SHADOW,
    _grade_parchment,
    _remap_luminance_value,
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


if __name__ == "__main__":
    unittest.main()
