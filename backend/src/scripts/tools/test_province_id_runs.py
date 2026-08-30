"""Tests for the run-length province index (province_id_runs.bin.gz)."""

import os
import struct
import tempfile
import unittest

import numpy as np

from ..province_id_grid import (
    RUNS_BBOX_ENTRY_SIZE,
    RUNS_HEADER_SIZE,
    RUNS_MAGIC,
    build_province_id_runs,
    deserialize_province_id_runs,
    read_province_id_runs_file,
    runs_to_province_id_grid,
    serialize_province_id_runs,
)

GRID_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "defines",
    "main",
    "province_id_grid.bin.gz",
)


def _grid(rows):
    arr = np.array(rows, dtype=np.uint16)
    return arr.shape[1], arr.shape[0], arr


class TestProvinceIdRuns(unittest.TestCase):
    def test_runs_never_cross_row_boundary(self):
        # A single id filling every pixel must still produce one run per row.
        width, height, ids = _grid([[7, 7, 7], [7, 7, 7]])
        lengths, run_ids, _bbox = build_province_id_runs(width, height, ids)

        self.assertEqual(list(lengths), [3, 3])
        self.assertEqual(list(run_ids), [7, 7])

    def test_run_split_within_row(self):
        width, height, ids = _grid([[1, 1, 2, 0], [0, 0, 3, 3]])
        lengths, run_ids, _bbox = build_province_id_runs(width, height, ids)

        self.assertEqual(list(lengths), [2, 1, 1, 2, 2])
        self.assertEqual(list(run_ids), [1, 2, 0, 0, 3])
        self.assertEqual(int(lengths.sum()), width * height)

    def test_bbox_table_is_inclusive_and_sorted(self):
        width, height, ids = _grid(
            [
                [0, 5, 5, 0],
                [0, 0, 5, 0],
                [9, 0, 0, 0],
            ]
        )
        _lengths, _run_ids, bbox = build_province_id_runs(width, height, ids)

        self.assertEqual([int(r[0]) for r in bbox], [5, 9])
        # province 5 spans x 1..2, y 0..1
        self.assertEqual([int(v) for v in bbox[0]], [5, 1, 0, 2, 1])
        # province 9 is the single pixel (0, 2)
        self.assertEqual([int(v) for v in bbox[1]], [9, 0, 2, 0, 2])

    def test_bbox_excludes_zero(self):
        width, height, ids = _grid([[0, 0], [0, 0]])
        _lengths, _run_ids, bbox = build_province_id_runs(width, height, ids)
        self.assertEqual(bbox.shape, (0, 5))

    def test_header_layout_and_payload_size(self):
        width, height, ids = _grid([[1, 1, 2], [2, 2, 2]])
        payload = serialize_province_id_runs(width, height, ids)

        magic, version, w, h, run_count, province_count, r0, r1 = struct.unpack(
            "<4sIiiIIII", payload[:RUNS_HEADER_SIZE]
        )
        self.assertEqual(magic, RUNS_MAGIC)
        self.assertEqual(version, 1)
        self.assertEqual((w, h), (width, height))
        self.assertEqual(run_count, 3)  # [1,1] [2] | [2,2,2]
        self.assertEqual(province_count, 2)
        self.assertEqual((r0, r1), (0, 0))
        self.assertEqual(
            len(payload),
            RUNS_HEADER_SIZE
            + run_count * 6
            + province_count * RUNS_BBOX_ENTRY_SIZE,
        )

    def test_planar_sections(self):
        width, height, ids = _grid([[1, 1, 2], [2, 2, 2]])
        payload = serialize_province_id_runs(width, height, ids)
        run_count = 3

        ids_start = RUNS_HEADER_SIZE + run_count * 4
        lengths = np.frombuffer(payload[RUNS_HEADER_SIZE:ids_start], dtype="<u4")
        run_ids = np.frombuffer(
            payload[ids_start : ids_start + run_count * 2], dtype="<u2"
        )
        self.assertEqual(list(lengths), [2, 1, 3])
        self.assertEqual(list(run_ids), [1, 2, 2])

    def test_roundtrip_expands_to_original_grid(self):
        rng = np.random.default_rng(1234)
        width, height = 37, 23
        ids = rng.integers(0, 6, size=(height, width), dtype=np.uint16)

        payload = serialize_province_id_runs(width, height, ids)
        w, h, lengths, run_ids, _bbox = deserialize_province_id_runs(payload)
        back = runs_to_province_id_grid(w, h, lengths, run_ids)

        self.assertEqual((w, h), (width, height))
        np.testing.assert_array_equal(back, ids)

    def test_roundtrip_file(self):
        import gzip

        width, height, ids = _grid([[4, 4, 0], [0, 8, 8]])
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "runs.bin.gz")
            with gzip.open(path, "wb") as f:
                f.write(serialize_province_id_runs(width, height, ids))

            w, h, lengths, run_ids, bbox = read_province_id_runs_file(path)

        self.assertEqual((w, h), (width, height))
        np.testing.assert_array_equal(
            runs_to_province_id_grid(w, h, lengths, run_ids), ids
        )
        self.assertEqual([int(r[0]) for r in bbox], [4, 8])

    def test_rejects_bad_magic(self):
        width, height, ids = _grid([[1, 2]])
        payload = bytearray(serialize_province_id_runs(width, height, ids))
        payload[0:4] = b"XXXX"
        with self.assertRaises(ValueError):
            deserialize_province_id_runs(bytes(payload))

    def test_rejects_bad_version(self):
        width, height, ids = _grid([[1, 2]])
        payload = bytearray(serialize_province_id_runs(width, height, ids))
        payload[4:8] = struct.pack("<I", 99)
        with self.assertRaises(ValueError):
            deserialize_province_id_runs(bytes(payload))

    def test_rejects_truncated_payload(self):
        width, height, ids = _grid([[1, 2, 3]])
        payload = serialize_province_id_runs(width, height, ids)
        with self.assertRaises(ValueError):
            deserialize_province_id_runs(payload[:-4])

    def test_rejects_short_header(self):
        with self.assertRaises(ValueError):
            deserialize_province_id_runs(b"PRUV")

    def test_rejects_pixel_count_mismatch(self):
        # Corrupt one length so the runs no longer cover width*height.
        width, height, ids = _grid([[1, 1, 2], [2, 2, 2]])
        payload = bytearray(serialize_province_id_runs(width, height, ids))
        payload[RUNS_HEADER_SIZE : RUNS_HEADER_SIZE + 4] = struct.pack("<I", 5)
        with self.assertRaises(ValueError):
            deserialize_province_id_runs(bytes(payload))

    @unittest.skipUnless(os.path.isfile(GRID_PATH), "main province grid not present")
    def test_matches_real_main_grid_exactly(self):
        """Equivalence against the real 6400x6400 artifact (read-only)."""
        from ..province_id_grid import read_province_id_grid_file

        width, height, ids = read_province_id_grid_file(GRID_PATH)
        payload = serialize_province_id_runs(width, height, ids)
        w, h, lengths, run_ids, bbox = deserialize_province_id_runs(payload)

        self.assertEqual((w, h), (width, height))
        np.testing.assert_array_equal(
            runs_to_province_id_grid(w, h, lengths, run_ids), ids
        )
        # Every non-zero id in the grid has a bbox row, and vice versa.
        grid_ids = set(int(v) for v in np.unique(ids) if v > 0)
        self.assertEqual(grid_ids, set(int(r[0]) for r in bbox))


if __name__ == "__main__":
    unittest.main()
