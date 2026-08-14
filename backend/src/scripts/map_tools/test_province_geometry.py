import unittest

from PIL import Image

from .province_geometry import (
    scan_province_image,
    serialize_centroids,
    serialize_neighbors,
    validate_geometry,
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


if __name__ == "__main__":
    unittest.main()
