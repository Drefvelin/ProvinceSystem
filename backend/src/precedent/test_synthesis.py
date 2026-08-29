"""Unit tests for Claude precedent synthesis (anthropic client fully mocked)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import anthropic

_BACKEND_SRC = Path(__file__).resolve().parents[1]
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

import precedent.synthesis as synthesis  # noqa: E402


class SynthesizeTest(unittest.TestCase):
    @mock.patch("precedent.synthesis.anthropic.Anthropic")
    def test_no_matches_short_circuits(self, mock_client_cls) -> None:
        result = synthesis.synthesize("query", [])

        self.assertEqual(result, synthesis._NO_MATCHES)
        mock_client_cls.assert_not_called()

    @mock.patch.dict("os.environ", {}, clear=True)
    @mock.patch("precedent.synthesis.anthropic.Anthropic")
    def test_missing_api_key(self, mock_client_cls) -> None:
        with self.assertRaises(synthesis.SynthesisError):
            synthesis.synthesize("query", [{"summary": "x"}])
        mock_client_cls.assert_not_called()

    @mock.patch.dict("os.environ", {"ANTHROPIC_API_KEY": "key"}, clear=True)
    @mock.patch("precedent.synthesis._load_rules", return_value="Rule 1.1: no bullying")
    @mock.patch("precedent.synthesis.anthropic.Anthropic")
    def test_success_strips_em_dash_and_includes_rules(
        self, mock_client_cls, mock_load_rules
    ) -> None:
        client = mock.MagicMock()
        client.messages.create.return_value = SimpleNamespace(
            content=[SimpleNamespace(type="text", text="Precedent suggests — a warning.")]
        )
        mock_client_cls.return_value = client

        result = synthesis.synthesize("query", [{"summary": "x", "distance": 0.1}])

        self.assertNotIn("—", result)
        self.assertIn(",  a warning.", result)
        _, kwargs = client.messages.create.call_args
        self.assertIn("Rule 1.1: no bullying", kwargs["system"])

    @mock.patch.dict("os.environ", {"ANTHROPIC_API_KEY": "key"}, clear=True)
    @mock.patch("precedent.synthesis.anthropic.Anthropic")
    def test_api_error_wrapped(self, mock_client_cls) -> None:
        client = mock.MagicMock()
        client.messages.create.side_effect = anthropic.APIError(
            "boom", request=mock.MagicMock(), body=None
        )
        mock_client_cls.return_value = client

        with self.assertRaises(synthesis.SynthesisError):
            synthesis.synthesize("query", [{"summary": "x"}])


if __name__ == "__main__":
    unittest.main()
