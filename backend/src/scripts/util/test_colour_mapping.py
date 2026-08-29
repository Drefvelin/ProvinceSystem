import unittest

from .colour_mapping import apply_occupation_remap


class OccupationRemapTests(unittest.TestCase):
    def test_remaps_occupied_province_to_occupier_rgb(self) -> None:
        de_jure = (10, 20, 30)
        occupier = (200, 10, 10)
        province_rgb = (1, 2, 3)
        province_to_color = {province_rgb: de_jure}
        provinces = {province_rgb: 17}
        nations = {
            "host": {"rgb": "10,20,30"},
            "atk": {"rgb": "200,10,10"},
        }
        province_data = [{"id": 17, "occupied_by": "atk"}]

        occupied = apply_occupation_remap(
            province_to_color, provinces, nations, province_data
        )

        self.assertEqual(province_to_color[province_rgb], occupier)
        self.assertEqual(occupied, {province_rgb})

    def test_ignores_unknown_occupier(self) -> None:
        province_rgb = (1, 2, 3)
        de_jure = (10, 20, 30)
        province_to_color = {province_rgb: de_jure}
        occupied = apply_occupation_remap(
            province_to_color,
            {province_rgb: 17},
            {"host": {"rgb": "10,20,30"}},
            [{"id": 17, "occupied_by": "missing"}],
        )
        self.assertEqual(province_to_color[province_rgb], de_jure)
        self.assertEqual(occupied, set())

    def test_empty_data_is_noop(self) -> None:
        self.assertEqual(apply_occupation_remap({}, {}, {}, None), set())
        self.assertEqual(apply_occupation_remap({}, {}, {}, []), set())


if __name__ == "__main__":
    unittest.main()
