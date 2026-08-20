"""Shared fort ZOC path helpers."""

from __future__ import annotations

import re

_SAFE_FORT_ID = re.compile(r"^[\w\-]+$")


def safe_fort_filename(fort_id: str) -> str | None:
    if not fort_id or not isinstance(fort_id, str):
        return None
    fort_id = fort_id.strip()
    if not fort_id or not _SAFE_FORT_ID.match(fort_id):
        return None
    return fort_id
