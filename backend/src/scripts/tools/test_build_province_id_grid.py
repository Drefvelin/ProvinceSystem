import json
import os
import tempfile
import unittest

import numpy as np

from ..province_id_grid import (
    build_province_id_map,
    deserialize_province_id_grid,
    lookup_at,
    read_province_id_grid_file,
    serialize_province_id_grid,
    write_province_id_grid_file,
)
from ..util.dirs import defines_file, input_file
from ..util.imagechecker import find_province


class TestProvinceIdGrid(unittest.TestCase):
    def test_roundtrip_small_grid(self):
        width, height = 3, 2
        ids = np.array([[1, 2, 0], [0, 3, 4]], dtype=np.uint16)
        payload = serialize_province_id_grid(width, height, ids)

        w2, h2, ids2 = deserialize_province_id_grid(payload)
        self.assertEqual((w2, h2), (width, height))
        np.testing.assert_array_equal(ids2, ids)

    def test_roundtrip_file(self):
        width, height = 2, 2
        ids = np.array([[10, 20], [30, 0]], dtype=np.uint16)

        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "grid.bin.gz")
            payload = serialize_province_id_grid(width, height, ids)
            import gzip

            with gzip.open(path, "wb") as f:
                f.write(payload)

            w2, h2, ids2 = read_province_id_grid_file(path)
            self.assertEqual((w2, h2), (width, height))
            np.testing.assert_array_equal(ids2, ids)

    def test_header_layout(self):
        width, height = 4, 3
        ids = np.zeros((height, width), dtype=np.uint16)
        payload = serialize_province_id_grid(width, height, ids)
        import struct

        w, h = struct.unpack("<ii", payload[:8])
        self.assertEqual((w, h), (width, height))
        self.assertEqual(len(payload), 8 + width * height * 2)

    def test_lookup_at_bounds(self):
        ids = np.array([[5, 6]], dtype=np.uint16)
        self.assertEqual(lookup_at(ids, 2, 0, 0), 5)
        self.assertEqual(lookup_at(ids, 2, 1, 0), 6)
        self.assertEqual(lookup_at(ids, 2, -1, 0), 0)
        self.assertEqual(lookup_at(ids, 2, 2, 0), 0)
        self.assertEqual(lookup_at(ids, 2, 0, 1), 0)

    def test_build_matches_find_province(self):
        if not os.path.isfile(input_file("main", "provinces.png")):
            self.skipTest("input/main/provinces.png not available")

        width, height, ids = build_province_id_map("main")
        self.assertGreater(width, 0)
        self.assertGreater(height, 0)

        centroids_path = defines_file("main", "province_centroids.json")
        if not os.path.isfile(centroids_path):
            self.skipTest("province_centroids.json not available")

        with open(centroids_path, encoding="utf-8") as f:
            centroids = json.load(f)

        samples = []
        for pid_str, meta in list(centroids.items())[:10]:
            x = int(round(meta["x"]))
            z = int(round(meta["y"]))
            samples.append((x, z, int(pid_str)))

        for x, z, expected_pid in samples:
            if x < 0 or z < 0 or x >= width or z >= height:
                continue
            grid_pid = lookup_at(ids, width, x, z)
            api_pid = find_province("main", x, z)
            self.assertEqual(
                grid_pid,
                api_pid,
                f"mismatch at ({x},{z}): grid={grid_pid} api={api_pid} expected~{expected_pid}",
            )
            if api_pid != 0:
                self.assertEqual(grid_pid, expected_pid)

    def test_write_default_path(self):
        if not os.path.isfile(input_file("main", "provinces.png")):
            self.skipTest("input/main/provinces.png not available")

        with tempfile.TemporaryDirectory() as tmp:
            # Write to temp via explicit dest to avoid mutating repo defines in unit test
            dest = os.path.join(tmp, "province_id_grid.bin.gz")
            path = write_province_id_grid_file("main", dest=dest)
            self.assertEqual(path, dest)
            self.assertTrue(os.path.isfile(path))

            w, h, ids = read_province_id_grid_file(path)
            self.assertGreater(w * h, 0)
            self.assertEqual(ids.shape, (h, w))


if __name__ == "__main__":
    unittest.main()
