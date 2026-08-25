"""Shared Minecraft name-colour token validation (#RRGGBB / §c)."""

from __future__ import annotations

import re
from typing import Final

_HEX_RE: Final = re.compile(r"^#?[0-9A-Fa-f]{6}$")
_LEGACY_RE: Final = re.compile(r"^[\u00a7&][0-9A-Fa-fk-or]$", re.IGNORECASE)

# Web preview / skins parity hard cap (ascended config may be higher).
MAX_NAME_COLOURS: Final = 8


class NameColourError(ValueError):
    """Invalid name colour list or token."""


def normalize_colour_token(token: str) -> str:
    t = (token or "").strip()
    if not t:
        raise NameColourError("empty colour token")
    if _HEX_RE.match(t):
        h = t if t.startswith("#") else f"#{t}"
        return h.lower()
    if t.startswith("&") and len(t) == 2:
        t = "\u00a7" + t[1]
    if _LEGACY_RE.match(t) or (len(t) == 2 and t[0] in ("\u00a7", "&")):
        return "\u00a7" + t[-1].lower()
    raise NameColourError(f"invalid colour '{token}' (use #RRGGBB or §c)")


def validate_name_colours(
    raw: list | None,
    *,
    max_colours: int = MAX_NAME_COLOURS,
) -> list[str]:
    """Normalize colour tokens; empty input → []. Raises NameColourError."""
    if not raw:
        return []
    if not isinstance(raw, list):
        raise NameColourError("name_colours must be a list")
    out: list[str] = []
    for item in raw:
        out.append(normalize_colour_token(str(item)))
    cap = max(0, int(max_colours))
    if len(out) > cap:
        raise NameColourError(f"at most {cap} name colours")
    return out


def effective_colour_cap(stops: int) -> int:
    """Player stops clamped to the web hard cap."""
    try:
        n = int(stops)
    except (TypeError, ValueError):
        n = 0
    return max(0, min(n, MAX_NAME_COLOURS))
