"""Last-seen SF chapter slug/name, stamped onto the live URL map.

Distinct from ledger ``map_id`` and from ``maps.yml`` ids. A chapter slug that
happens to match a registered map is still just a label; it never routes an
upload and never 409s.
"""

from __future__ import annotations

import json
import os
import re

from ..util.dirs import input_file

UNKNOWN_ID = "unknown"
UNKNOWN_NAME = "Unknown"

_CHAPTER_ID_RE = re.compile(r"[a-z0-9]+")

CHAPTER_IDENTITY_FILENAME = "chapter_identity.json"


def normalize_id(raw) -> str:
    if not isinstance(raw, str):
        return UNKNOWN_ID
    chapter_id = raw.strip().lower()
    if not chapter_id or _CHAPTER_ID_RE.fullmatch(chapter_id) is None:
        return UNKNOWN_ID
    return chapter_id


def normalize_name(raw) -> str:
    if not isinstance(raw, str):
        return UNKNOWN_NAME
    name = raw.strip()
    return name if name else UNKNOWN_NAME


def identity_from_payload(payload) -> dict[str, str]:
    """Missing or invalid keys become unknown / Unknown. Extra keys ignored."""
    if not isinstance(payload, dict):
        return {"chapter_id": UNKNOWN_ID, "chapter_name": UNKNOWN_NAME}
    return {
        "chapter_id": normalize_id(payload.get("chapter_id")),
        "chapter_name": normalize_name(payload.get("chapter_name")),
    }


def write_chapter_identity(map_id: str, payload) -> dict[str, str]:
    """Overwrite ``input/{map_id}/chapter_identity.json`` for this live map."""
    identity = identity_from_payload(payload)
    path = input_file(map_id, CHAPTER_IDENTITY_FILENAME)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(identity, f, ensure_ascii=False, indent=2)
    return identity


def read_chapter_identity(map_id: str) -> dict[str, str] | None:
    """Last stamp for this live map, or None if missing/unreadable."""
    path = input_file(map_id, CHAPTER_IDENTITY_FILENAME)
    try:
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return identity_from_payload(payload)


def overlay_live_chapter(public: dict) -> dict:
    """Attach last-seen chapter keys on live maps; never rewrite archived titles.

    ``display_name`` becomes the chapter name only when both slug and name are
    known. ``unknown`` / ``Unknown`` stay attached for later Archive prefill
    but must not replace the yaml label.
    """
    out = dict(public)
    if out.get("archived"):
        out.pop("chapter_id", None)
        out.pop("chapter_name", None)
        return out

    identity = read_chapter_identity(str(out.get("id") or ""))
    if identity is None:
        chapter_id, chapter_name = UNKNOWN_ID, UNKNOWN_NAME
    else:
        chapter_id = identity["chapter_id"]
        chapter_name = identity["chapter_name"]
    out["chapter_id"] = chapter_id
    out["chapter_name"] = chapter_name
    if chapter_id != UNKNOWN_ID and chapter_name != UNKNOWN_NAME:
        out["display_name"] = chapter_name
    return out
