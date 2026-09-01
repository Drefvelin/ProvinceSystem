"""Tests for the crash-safe write helper in `scripts/util/atomic.py`."""

from __future__ import annotations

import os
import tempfile
import unittest
from unittest.mock import patch

from . import atomic


class TestWriteAtomicChmod(unittest.TestCase):
    """Finding 2: mkstemp creates 0600; the write must respect the umask instead."""

    def test_chmod_is_applied_with_umask_default_bits(self):
        # POSIX semantics, mocked so the assertion is platform-independent: a
        # umask of 022 should leave the file 0644 (0o666 & ~0o022).
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "out.bin")
            chmod_calls = []

            def spy_chmod(target, mode):
                chmod_calls.append((target, mode))

            with patch.object(atomic, "_UMASK", 0o022), patch.object(
                atomic.os, "chmod", side_effect=spy_chmod
            ):
                atomic._write_atomic(path, b"payload")

            self.assertEqual(len(chmod_calls), 1)
            tmp_path, mode = chmod_calls[0]
            self.assertEqual(mode, 0o644)
            # chmod must run on the temp sibling before the rename, not the
            # final path (the rename target may not exist yet at that point).
            self.assertNotEqual(tmp_path, path)
            self.assertTrue(os.path.isfile(path))
            with open(path, "rb") as f:
                self.assertEqual(f.read(), b"payload")

    def test_chmod_failure_does_not_lose_the_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "out.bin")
            with patch.object(
                atomic.os, "chmod", side_effect=OSError("no chmod here")
            ):
                atomic._write_atomic(path, b"payload")
            self.assertTrue(os.path.isfile(path))
            with open(path, "rb") as f:
                self.assertEqual(f.read(), b"payload")

    def test_read_umask_restores_the_process_umask(self):
        # _read_umask must not leave the process umask changed as a side effect.
        before = os.umask(0o007)
        os.umask(before)
        observed = atomic._read_umask()
        after = os.umask(0o007)
        os.umask(after)
        self.assertEqual(before, after)
        self.assertEqual(observed, before)


class TestWriteAtomicNoPartialFile(unittest.TestCase):
    """Finding 1's underlying primitive: no truncated/partial file is ever visible."""

    def test_no_temp_sibling_survives_a_successful_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "out.bin")
            atomic._write_atomic(path, b"hello world")
            entries = os.listdir(tmp)
            self.assertEqual(entries, ["out.bin"])

    def test_a_failure_before_replace_leaves_no_destination_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "out.bin")
            with patch.object(
                atomic.os, "fsync", side_effect=OSError("disk gone")
            ):
                with self.assertRaises(OSError):
                    atomic._write_atomic(path, b"hello world")
            # Neither a truncated destination file nor a leftover temp sibling.
            self.assertEqual(os.listdir(tmp), [])

    def test_second_writer_does_not_corrupt_the_first(self):
        # Regression for the reason a *unique* temp name is used rather than a
        # fixed `<path>.tmp`: two concurrent writers must not interleave.
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "out.bin")
            atomic._write_atomic(path, b"first")
            atomic._write_atomic(path, b"second")
            with open(path, "rb") as f:
                self.assertEqual(f.read(), b"second")
            self.assertEqual(os.listdir(tmp), ["out.bin"])


if __name__ == "__main__":
    unittest.main()
