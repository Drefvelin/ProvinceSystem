import colorsys
import unittest

from .display_colour import (
    PAPER_HIGH,
    display_rgb,
    hover_rgb,
    occupation_display_rgb,
    parchment_wash_rgb,
)


class DisplayColourTests(unittest.TestCase):
    def test_display_rgb_mutes_saturated_input(self):
        raw = (255, 0, 0)
        muted = display_rgb(raw)
        self.assertNotEqual(raw, muted)

    def test_hover_rgb_brighter_than_display(self):
        raw = (40, 120, 200)
        muted = display_rgb(raw)
        hover = hover_rgb(raw)
        self.assertGreater(sum(hover), sum(muted))

    def test_pick_invariant_display_is_transform_of_raw(self):
        raw = (90, 45, 210)
        self.assertEqual(display_rgb(raw), display_rgb(raw))
        self.assertNotEqual(raw, display_rgb(raw))

    def test_nimbus_stays_blue_family(self):
        nimbus = (59, 53, 211)
        r, g, b = parchment_wash_rgb(nimbus)
        self.assertGreater(b, r)
        self.assertGreater(b, g)

    def test_drakhanate_stays_red_family(self):
        drakhanate = (111, 0, 0)
        r, g, b = parchment_wash_rgb(drakhanate)
        self.assertGreater(r, g)
        self.assertGreater(r, b)

    def test_red_and_blue_remain_distinct(self):
        red = display_rgb((255, 0, 0))
        blue = display_rgb((0, 0, 255))
        self.assertNotEqual(red, blue)
        red_h, _, _ = colorsys.rgb_to_hls(*(c / 255.0 for c in red))
        blue_h, _, _ = colorsys.rgb_to_hls(*(c / 255.0 for c in blue))
        self.assertLess(red_h, 0.2)
        self.assertGreater(blue_h, 0.55)

    def test_neon_desaturated(self):
        raw = (255, 0, 0)
        _, _, raw_s = colorsys.rgb_to_hls(*(c / 255.0 for c in raw))
        washed = parchment_wash_rgb(raw)
        _, _, washed_s = colorsys.rgb_to_hls(*(c / 255.0 for c in washed))
        self.assertLess(washed_s, raw_s)

    def test_dark_nation_not_flat_black(self):
        toned = display_rgb((30, 25, 20))
        self.assertGreater(sum(toned), 120)

    def test_hover_brighter_in_hsl(self):
        raw = (120, 40, 180)
        base = display_rgb(raw)
        hover = hover_rgb(raw)
        _, base_l, _ = colorsys.rgb_to_hls(*(c / 255.0 for c in base))
        _, hover_l, _ = colorsys.rgb_to_hls(*(c / 255.0 for c in hover))
        self.assertGreater(hover_l, base_l)

    def test_occupation_display_is_uint8_and_closer_to_parchment(self):
        raw = (200, 20, 20)
        occupied = occupation_display_rgb(raw)
        home = display_rgb(raw)
        for channel in occupied:
            self.assertIsInstance(channel, int)
            self.assertGreaterEqual(channel, 0)
            self.assertLessEqual(channel, 255)
        self.assertNotEqual(occupied, home)
        self.assertLess(
            _rgb_distance(occupied, PAPER_HIGH),
            _rgb_distance(home, PAPER_HIGH) * 0.7,
        )


def _rgb_distance(a, b):
    return sum((a[i] - b[i]) ** 2 for i in range(3))


if __name__ == "__main__":
    unittest.main()
