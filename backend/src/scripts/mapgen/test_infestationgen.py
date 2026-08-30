import unittest

from .infestationgen import SEVERITY_RGBA, infestation_to_rgba


class InfestationColorTests(unittest.TestCase):
    def test_four_severities_yellow_to_dark_red(self) -> None:
        mild = infestation_to_rgba("mild")
        worrying = infestation_to_rgba("worrying")
        severe = infestation_to_rgba("severe")
        extreme = infestation_to_rgba("extreme")
        self.assertIsNotNone(mild)
        self.assertIsNotNone(worrying)
        self.assertIsNotNone(severe)
        self.assertIsNotNone(extreme)
        self.assertEqual(mild, SEVERITY_RGBA["mild"])
        self.assertGreater(mild[1], severe[1])
        self.assertGreater(mild[0] + mild[1], extreme[0] + extreme[1])
        self.assertEqual(extreme[1], 0)
        self.assertEqual(extreme[2], 0)

    def test_no_green_channel_dominance(self) -> None:
        for key, rgba in SEVERITY_RGBA.items():
            with self.subTest(severity=key):
                r, g, b, a = rgba
                self.assertLessEqual(g, r)
                self.assertLess(g, 210)
                self.assertEqual(b, 0 if key == "extreme" else b)
                self.assertTrue(0 <= r <= 255)
                self.assertTrue(0 <= a <= 255)

    def test_unknown_severity_is_none(self) -> None:
        self.assertIsNone(infestation_to_rgba("legendary"))
        self.assertIsNone(infestation_to_rgba(""))


if __name__ == "__main__":
    unittest.main()
