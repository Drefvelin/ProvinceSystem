import unittest

from PIL import Image

from .province_geometry import (
    build_bridge_grid,
    build_label_grid,
    build_label_neighbors,
    scan_province_image,
    serialize_centroids,
    serialize_neighbors,
    validate_geometry,
    validate_label_neighbors,
)


class ProvinceGeometryTests(unittest.TestCase):
    def _image_from_rgb_grid(self, rows: list[list[tuple[int, int, int]]]) -> Image.Image:
        height = len(rows)
        width = len(rows[0])
        img = Image.new("RGB", (width, height))
        pixels = img.load()
        for y, row in enumerate(rows):
            self.assertEqual(len(row), width)
            for x, rgb in enumerate(row):
                pixels[x, y] = rgb
        return img

    def test_horizontal_strip_neighbors_and_centroids(self):
        color_to_id = {
            (255, 0, 0): 1,
            (0, 255, 0): 2,
            (0, 0, 255): 3,
        }
        img = self._image_from_rgb_grid(
            [
                [(255, 0, 0), (0, 255, 0), (0, 0, 255)],
            ]
        )

        neighbors, centroids = scan_province_image(img, color_to_id)

        self.assertEqual(neighbors[1], {2})
        self.assertEqual(neighbors[2], {1, 3})
        self.assertEqual(neighbors[3], {2})
        self.assertEqual(centroids[1]["x"], 0.0)
        self.assertEqual(centroids[2]["x"], 1.0)
        self.assertEqual(centroids[3]["x"], 2.0)
        self.assertEqual(centroids[1]["pixel_count"], 1)

    def test_two_pixels_same_province_centroid(self):
        color_to_id = {(255, 0, 0): 10}
        img = self._image_from_rgb_grid(
            [
                [(0, 0, 0), (255, 0, 0)],
                [(255, 0, 0), (0, 0, 0)],
            ]
        )

        neighbors, centroids = scan_province_image(img, color_to_id)

        self.assertEqual(neighbors, {})
        self.assertEqual(centroids[10]["x"], 0.5)
        self.assertEqual(centroids[10]["y"], 0.5)
        self.assertEqual(centroids[10]["pixel_count"], 2)

    def test_black_and_unknown_rgb_ignored(self):
        color_to_id = {(255, 0, 0): 1}
        img = self._image_from_rgb_grid(
            [
                [(0, 0, 0), (255, 255, 255), (255, 0, 0)],
            ]
        )

        neighbors, centroids = scan_province_image(img, color_to_id)

        self.assertEqual(neighbors, {})
        self.assertEqual(set(centroids), {1})

    def test_validate_geometry_symmetry_and_missing(self):
        neighbors = {1: {2}, 2: {1}}
        centroids = {
            1: {"x": 0.0, "y": 0.0, "pixel_count": 1},
            2: {"x": 1.0, "y": 0.0, "pixel_count": 1},
        }
        warnings = validate_geometry({1, 2}, neighbors, centroids)
        self.assertEqual(warnings, [])

        with self.assertRaises(ValueError):
            validate_geometry({1, 2, 3}, neighbors, centroids)

        asymmetric = {1: {2}, 2: set()}
        with self.assertRaises(ValueError):
            validate_geometry({1, 2}, asymmetric, centroids)

    def test_serialization_uses_string_keys(self):
        neighbors = {5: {6, 7}, 6: {5}}
        centroids = {5: {"x": 1.5, "y": 2.0, "pixel_count": 3}}

        self.assertEqual(serialize_neighbors(neighbors)["5"], [6, 7])
        self.assertEqual(serialize_centroids(centroids)["5"]["pixel_count"], 3)

    def test_build_label_grid_picks_dominant_province_per_cell(self):
        color_to_id = {
            (255, 0, 0): 1,
            (0, 255, 0): 2,
            (0, 0, 255): 3,
        }
        img = self._image_from_rgb_grid(
            [
                [(255, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)],
                [(255, 0, 0), (0, 255, 0), (0, 255, 0), (0, 0, 255)],
                [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)],
            ]
        )

        cells, meta = build_label_grid(img, color_to_id, grid_width=4)

        self.assertEqual(meta["mapWidth"], 4)
        self.assertEqual(meta["mapHeight"], 3)
        self.assertEqual(meta["gridWidth"], 4)
        self.assertEqual(meta["gridHeight"], 3)
        self.assertEqual(cells[0], 1)
        self.assertEqual(cells[1], 1)
        self.assertEqual(cells[5], 2)
        self.assertEqual(cells[11], 0)

    def test_build_label_grid_treats_water_terrain_as_sea(self):
        color_to_id = {
            (255, 0, 0): 1,
            (0, 255, 0): 2,
        }
        img = self._image_from_rgb_grid(
            [
                [(255, 0, 0), (0, 255, 0), (0, 255, 0)],
            ]
        )
        terrains = {1: "plains", 2: "water"}

        cells, _meta = build_label_grid(
            img, color_to_id, terrains, grid_width=3
        )

        self.assertEqual(cells[0], 1)
        self.assertEqual(cells[1], 0)
        self.assertEqual(cells[2], 0)

    def test_label_neighbors_bridge_across_black_gap(self):
        color_to_id = {
            (255, 0, 0): 1,
            (0, 255, 0): 2,
        }
        img = self._image_from_rgb_grid(
            [
                [(255, 0, 0), (0, 0, 0), (0, 255, 0)],
            ]
        )
        strict_neighbors, _centroids = scan_province_image(img, color_to_id)
        bridge_grid, max_steps = build_bridge_grid(img, color_to_id, {}, grid_width=3)
        label_neighbors = build_label_neighbors(
            bridge_grid, max_steps, strict_neighbors
        )

        self.assertEqual(strict_neighbors.get(1, set()), set())
        self.assertEqual(label_neighbors[1], {2})
        self.assertEqual(label_neighbors[2], {1})
        validate_label_neighbors({1, 2}, strict_neighbors, label_neighbors)

    def test_label_neighbors_blocked_by_land_province(self):
        color_to_id = {
            (255, 0, 0): 1,
            (255, 255, 0): 99,
            (0, 255, 0): 2,
        }
        rows = [[(255, 0, 0)] + [(0, 0, 0)] * 3 + [(255, 255, 0)] + [(0, 0, 0)] * 3 + [(0, 255, 0)]]
        img = self._image_from_rgb_grid(rows)
        strict_neighbors, _centroids = scan_province_image(img, color_to_id)
        bridge_grid, max_steps = build_bridge_grid(img, color_to_id, {}, grid_width=9)
        label_neighbors = build_label_neighbors(
            bridge_grid, max_steps, strict_neighbors
        )

        self.assertNotIn(2, label_neighbors.get(1, set()))
        self.assertNotIn(1, label_neighbors.get(2, set()))

    def test_label_neighbors_gap_beyond_max_distance(self):
        from .province_geometry import LABEL_BRIDGE_MAX_PX

        color_to_id = {
            (255, 0, 0): 1,
            (0, 255, 0): 2,
        }
        gap = [(0, 0, 0)] * (LABEL_BRIDGE_MAX_PX + 20)
        img = self._image_from_rgb_grid(
            [
                [(255, 0, 0)] + gap + [(0, 255, 0)],
            ]
        )
        strict_neighbors, _centroids = scan_province_image(img, color_to_id)
        grid_width = len(gap) + 2
        bridge_grid, max_steps = build_bridge_grid(
            img, color_to_id, {}, grid_width=grid_width
        )
        label_neighbors = build_label_neighbors(
            bridge_grid, max_steps, strict_neighbors
        )

        self.assertNotIn(2, label_neighbors.get(1, set()))

    def test_label_neighbors_include_strict_edges(self):
        color_to_id = {
            (255, 0, 0): 1,
            (0, 255, 0): 2,
            (0, 0, 255): 3,
        }
        img = self._image_from_rgb_grid(
            [
                [(255, 0, 0), (0, 255, 0), (0, 0, 255)],
            ]
        )
        strict_neighbors, _centroids = scan_province_image(img, color_to_id)
        bridge_grid, max_steps = build_bridge_grid(img, color_to_id, {}, grid_width=3)
        label_neighbors = build_label_neighbors(
            bridge_grid, max_steps, strict_neighbors
        )

        for pid, nlist in strict_neighbors.items():
            self.assertTrue(nlist.issubset(label_neighbors.get(pid, set())))


if __name__ == "__main__":
    unittest.main()
