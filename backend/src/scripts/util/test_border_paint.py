import unittest

from PIL import Image

from .border_paint import (
    INK_DARK,
    OPAQUE_UNION_OWNER,
    apply_region_borders,
    border_color_for_fill,
    compute_border_owners,
    compute_opaque_union_borders,
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

    def test_opaque_union_outlines_single_fill_vs_transparent(self):
        width, height = 8, 8
        fill = (200, 100, 100)
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        pixels = img.load()
        for x in range(2, 6):
            for y in range(2, 6):
                pixels[x, y] = (*fill, 255)

        owners = compute_opaque_union_borders(pixels, width, height)
        edge = (2, 2)
        interior = (3, 3)
        self.assertIn(OPAQUE_UNION_OWNER, owners.get(edge, set()))
        self.assertNotIn(interior, owners)

        apply_region_borders(
            pixels,
            OPAQUE_UNION_OWNER,
            owners,
            width,
            height,
            INK_DARK,
            thickness=0,
        )
        self.assertEqual(pixels[2, 2], INK_DARK)
        self.assertEqual(pixels[3, 3][:3], fill)

    def test_opaque_union_ignores_two_tone_seam(self):
        width, height = 8, 8
        wash = (180, 80, 80)
        grey = (120, 70, 70)
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        pixels = img.load()
        for x in range(2, 4):
            for y in range(2, 6):
                pixels[x, y] = (*wash, 255)
        for x in range(4, 6):
            for y in range(2, 6):
                pixels[x, y] = (*grey, 255)

        owners = compute_opaque_union_borders(pixels, width, height)
        seam_left = (3, 3)
        seam_right = (4, 3)
        self.assertNotIn(seam_left, owners)
        self.assertNotIn(seam_right, owners)
        self.assertIn(OPAQUE_UNION_OWNER, owners.get((2, 3), set()))
        self.assertIn(OPAQUE_UNION_OWNER, owners.get((5, 3), set()))

        apply_region_borders(
            pixels,
            OPAQUE_UNION_OWNER,
            owners,
            width,
            height,
            INK_DARK,
            thickness=0,
        )
        self.assertEqual(pixels[3, 3][:3], wash)
        self.assertEqual(pixels[4, 3][:3], grey)
        self.assertEqual(pixels[2, 3], INK_DARK)
        self.assertEqual(pixels[5, 3], INK_DARK)


if __name__ == "__main__":
    unittest.main()
