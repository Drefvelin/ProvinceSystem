import unittest

from PIL import Image

from .border_paint import (
    INK_DARK,
    apply_region_borders,
    border_color_for_fill,
    compute_border_owners,
)


class BorderPaintTests(unittest.TestCase):
    def test_border_color_dark_fill_returns_dark_ink(self):
        self.assertEqual(border_color_for_fill((30, 25, 20)), INK_DARK)

    def test_border_color_light_fill_returns_dark_ink(self):
        self.assertEqual(border_color_for_fill((220, 210, 190)), INK_DARK)

    def test_border_color_uniform_for_washed_fills(self):
        dark_rgb = (100, 100, 100)
        light_rgb = (160, 160, 160)
        self.assertEqual(border_color_for_fill(dark_rgb), INK_DARK)
        self.assertEqual(border_color_for_fill(light_rgb), INK_DARK)

    def test_apply_region_borders_no_soften(self):
        width, height = 8, 8
        region_color = (200, 100, 100)
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        pixels = img.load()
        for x in range(2, 6):
            for y in range(2, 6):
                pixels[x, y] = (*region_color, 255)

        border_owners = compute_border_owners(pixels, width, height, include_outer=True)
        before = {
            (x, y): pixels[x, y]
            for x in range(width)
            for y in range(height)
            if pixels[x, y][3] != 0
        }

        apply_region_borders(
            pixels,
            region_color,
            border_owners,
            width,
            height,
            INK_DARK,
            thickness=1,
            soften=False,
        )

        soften_pixels = [
            (x, y)
            for x in range(width)
            for y in range(height)
            if pixels[x, y] == (0, 0, 0, 128)
        ]
        self.assertEqual(soften_pixels, [])
        after = {(x, y): pixels[x, y] for x, y in before}
        self.assertNotEqual(before, after)


if __name__ == "__main__":
    unittest.main()
