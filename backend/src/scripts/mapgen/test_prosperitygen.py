import unittest

import numpy as np

from .map_paint_numpy import paint_from_rgb_lut
from .prosperitygen import prosperity_to_alpha, prosperity_to_color


def _assert_rgba_channel(value: int) -> None:
    assert isinstance(value, int)
    assert 0 <= value <= 255


class ProsperityColorTests(unittest.TestCase):
    def test_color_and_alpha_stay_in_uint8_range(self) -> None:
        samples = [0.0, 0.33, 0.5, 0.66, 0.8, 1.0]
        samples.extend(np.linspace(0.0, 1.0, 101).tolist())

        for norm in samples:
            with self.subTest(norm=norm):
                r, g, b = prosperity_to_color(float(norm))
                a = prosperity_to_alpha(float(norm))
                for channel in (r, g, b, a):
                    _assert_rgba_channel(channel)

    def test_paint_from_rgb_lut_accepts_prosperity_colors(self) -> None:
        norms = [0.0, 0.33, 0.5, 0.66, 0.8, 1.0]
        provinces = np.zeros((1, len(norms), 4), dtype=np.uint8)
        lut: dict[tuple[int, int, int], tuple[int, int, int, int]] = {}
        expected = []

        for i, norm in enumerate(norms):
            rgb = (10 + i, 20, 30)
            provinces[0, i] = (*rgb, 255)
            color = (*prosperity_to_color(norm), prosperity_to_alpha(norm))
            lut[rgb] = color
            expected.append(color)

        painted = paint_from_rgb_lut(provinces, lut, skip_black=False)
        self.assertEqual(painted.dtype, np.uint8)
        self.assertEqual(painted.shape, (1, len(norms), 4))
        np.testing.assert_array_equal(
            painted[0],
            np.array(expected, dtype=np.uint8),
        )


if __name__ == "__main__":
    unittest.main()
