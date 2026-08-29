"""Unit tests for Voyage AI embedding calls (httpx fully mocked)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

import httpx

_BACKEND_SRC = Path(__file__).resolve().parents[1]
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

import precedent.embeddings as embeddings  # noqa: E402


class EmbedBatchTest(unittest.TestCase):
    @mock.patch.dict("os.environ", {}, clear=True)
    @mock.patch("precedent.embeddings.httpx.post")
    def test_missing_api_key(self, mock_post) -> None:
        with self.assertRaises(embeddings.EmbeddingError):
            embeddings.embed_batch(["hello"])
        mock_post.assert_not_called()

    @mock.patch.dict("os.environ", {"VOYAGE_API_KEY": "key"}, clear=True)
    @mock.patch("precedent.embeddings.httpx.post")
    def test_success(self, mock_post) -> None:
        resp = mock.MagicMock()
        resp.raise_for_status.return_value = None
        resp.json.return_value = {"data": [{"embedding": [0.1, 0.2]}]}
        mock_post.return_value = resp

        result = embeddings.embed_batch(["hello"])

        self.assertEqual(result, [[0.1, 0.2]])
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer key")

    @mock.patch.dict("os.environ", {"VOYAGE_API_KEY": "key"}, clear=True)
    @mock.patch("precedent.embeddings.httpx.post")
    def test_embed_single_returns_first_vector(self, mock_post) -> None:
        resp = mock.MagicMock()
        resp.raise_for_status.return_value = None
        resp.json.return_value = {"data": [{"embedding": [0.5]}]}
        mock_post.return_value = resp

        self.assertEqual(embeddings.embed("hello"), [0.5])

    @mock.patch.dict("os.environ", {"VOYAGE_API_KEY": "key"}, clear=True)
    @mock.patch("precedent.embeddings.httpx.post")
    def test_http_error_wrapped(self, mock_post) -> None:
        mock_post.side_effect = httpx.HTTPError("boom")

        with self.assertRaises(embeddings.EmbeddingError):
            embeddings.embed_batch(["hello"])

    @mock.patch.dict("os.environ", {"VOYAGE_API_KEY": "key"}, clear=True)
    @mock.patch("precedent.embeddings.httpx.post")
    def test_bad_response_shape_wrapped(self, mock_post) -> None:
        resp = mock.MagicMock()
        resp.raise_for_status.return_value = None
        resp.json.return_value = {}
        mock_post.return_value = resp

        with self.assertRaises(embeddings.EmbeddingError):
            embeddings.embed_batch(["hello"])


if __name__ == "__main__":
    unittest.main()
