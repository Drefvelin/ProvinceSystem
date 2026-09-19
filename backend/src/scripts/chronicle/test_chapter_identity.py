"""Normalize and persist last-seen SF chapter identity."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

_BACKEND_ROOT = Path(__file__).resolve().parents[3]
_BACKEND_SRC = _BACKEND_ROOT / "src"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

os.environ.setdefault("SKINS_DEV", "1")

from src.scripts.chronicle import chapter_identity as ident  # noqa: E402
from src.scripts.util import dirs  # noqa: E402


@pytest.mark.parametrize(
    "raw, expected",
    [
        (None, "unknown"),
        ("", "unknown"),
        ("   ", "unknown"),
        (123, "unknown"),
        ("Vardera", "vardera"),
        ("  MAIN  ", "main"),
        ("calavorn", "calavorn"),
        ("Vardera-1", "unknown"),
        ("va_rdera", "unknown"),
        ("värdera", "unknown"),
        ("a1b2", "a1b2"),
    ],
)
def test_normalize_id(raw, expected):
    assert ident.normalize_id(raw) == expected


@pytest.mark.parametrize(
    "raw, expected",
    [
        (None, "Unknown"),
        ("", "Unknown"),
        ("   ", "Unknown"),
        (12, "Unknown"),
        ("Vardera", "Vardera"),
        ("  Calavorn  ", "Calavorn"),
        ("Vardera-1", "Vardera-1"),
        ("värdera", "värdera"),
    ],
)
def test_normalize_name(raw, expected):
    assert ident.normalize_name(raw) == expected


def test_identity_from_payload_missing_keys():
    assert ident.identity_from_payload({}) == {
        "chapter_id": "unknown",
        "chapter_name": "Unknown",
    }
    assert ident.identity_from_payload(None) == {
        "chapter_id": "unknown",
        "chapter_name": "Unknown",
    }


def test_identity_from_payload_ignores_extra_keys():
    out = ident.identity_from_payload(
        {
            "chapter_id": "vardera",
            "chapter_name": "Vardera",
            "map_id": "main",
            "markers": [],
        }
    )
    assert out == {"chapter_id": "vardera", "chapter_name": "Vardera"}


def test_write_chapter_identity(tmp_path, monkeypatch):
    monkeypatch.setattr(dirs, "INPUT_DIR", str(tmp_path / "input"))
    ident.write_chapter_identity(
        "main", {"chapter_id": "Vardera", "chapter_name": "  Vardera  "}
    )
    path = tmp_path / "input" / "main" / "chapter_identity.json"
    assert json.loads(path.read_text(encoding="utf-8")) == {
        "chapter_id": "vardera",
        "chapter_name": "Vardera",
    }
    ident.write_chapter_identity("main", {})
    assert json.loads(path.read_text(encoding="utf-8")) == {
        "chapter_id": "unknown",
        "chapter_name": "Unknown",
    }


def test_read_chapter_identity_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(dirs, "INPUT_DIR", str(tmp_path / "input"))
    assert ident.read_chapter_identity("main") is None


def test_read_chapter_identity_corrupt(tmp_path, monkeypatch):
    monkeypatch.setattr(dirs, "INPUT_DIR", str(tmp_path / "input"))
    path = tmp_path / "input" / "main" / "chapter_identity.json"
    path.parent.mkdir(parents=True)
    path.write_text("{not-json", encoding="utf-8")
    assert ident.read_chapter_identity("main") is None
    path.write_text("[]", encoding="utf-8")
    assert ident.read_chapter_identity("main") is None


def test_overlay_live_known_replaces_display_name(tmp_path, monkeypatch):
    monkeypatch.setattr(dirs, "INPUT_DIR", str(tmp_path / "input"))
    ident.write_chapter_identity(
        "main", {"chapter_id": "vardera", "chapter_name": "Vardera"}
    )
    out = ident.overlay_live_chapter(
        {
            "id": "main",
            "display_name": "Adavaar",
            "public": True,
            "archived": False,
        }
    )
    assert out["display_name"] == "Vardera"
    assert out["chapter_id"] == "vardera"
    assert out["chapter_name"] == "Vardera"


def test_overlay_unknown_keeps_yaml_display_name(tmp_path, monkeypatch):
    monkeypatch.setattr(dirs, "INPUT_DIR", str(tmp_path / "input"))
    missing = ident.overlay_live_chapter(
        {
            "id": "main",
            "display_name": "Adavaar",
            "public": True,
            "archived": False,
        }
    )
    assert missing["display_name"] == "Adavaar"
    assert missing["chapter_id"] == "unknown"
    assert missing["chapter_name"] == "Unknown"

    ident.write_chapter_identity("main", {})
    stamped = ident.overlay_live_chapter(
        {
            "id": "main",
            "display_name": "Adavaar",
            "public": True,
            "archived": False,
        }
    )
    assert stamped["display_name"] == "Adavaar"
    assert stamped["chapter_id"] == "unknown"
    assert stamped["chapter_name"] == "Unknown"


def test_overlay_archived_ignores_stamp(tmp_path, monkeypatch):
    monkeypatch.setattr(dirs, "INPUT_DIR", str(tmp_path / "input"))
    ident.write_chapter_identity(
        "calavorn", {"chapter_id": "vardera", "chapter_name": "Vardera"}
    )
    out = ident.overlay_live_chapter(
        {
            "id": "calavorn",
            "display_name": "Calavorn",
            "public": True,
            "archived": True,
            "chapter_id": "should-drop",
        }
    )
    assert out["display_name"] == "Calavorn"
    assert "chapter_id" not in out
    assert "chapter_name" not in out
