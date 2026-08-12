"""Shared user-text validation (display names + prose).

Technical skin/id slugs stay in ``src.skins.naming``. This module is the
source of truth for free-text charset rules on the API; the frontend mirrors
the same patterns for UX only.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Final

# Letters (incl. accented), digits, plus these extras (checked via category).
_DISPLAY_ALLOWED_EXTRA: Final = frozenset(" .-'_")

# Minecraft / legacy colour tokens to reject on ingest.
_COLOUR_CODE_RE: Final = re.compile(
    r"(?:§.|[&][0-9A-Fa-fk-orK-OR]|#[0-9A-Fa-f]{6})"
)

# ASCII controls (newline handled separately for prose).
_CONTROL_RE: Final = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

DISPLAY_NAME_HINT: Final = (
    "letters, numbers, spaces, and - _ . '"
)


class TextValidationError(ValueError):
    """Invalid user-facing free text."""


def normalize_user_text(value: str | None, *, collapse_ws: bool = False) -> str:
    """NFKC + strip ends; optionally collapse internal whitespace."""
    s = unicodedata.normalize("NFKC", str(value or ""))
    s = s.strip()
    if collapse_ws:
        s = re.sub(r"\s+", " ", s)
    return s


def _has_disallowed_display_char(s: str) -> bool:
    for ch in s:
        if ch in _DISPLAY_ALLOWED_EXTRA:
            continue
        cat = unicodedata.category(ch)
        # L* letters, Nd decimal digits only (no emoji So/Sk, no symbols).
        if cat.startswith("L") or cat == "Nd":
            continue
        return True
    return False


def _label(field: str) -> str:
    return (field or "text").replace("_", " ").strip() or "text"


def assert_display_name(
    value: str | None,
    *,
    min_len: int,
    max_len: int,
    field: str = "name",
) -> str:
    """Validate a short identity-ish name; return normalized string."""
    s = normalize_user_text(value, collapse_ws=True)
    label = _label(field).capitalize()
    if not s:
        raise TextValidationError(f"{label} is required")
    if len(s) < min_len:
        raise TextValidationError(
            f"{label} must be at least {min_len} character"
            f"{'' if min_len == 1 else 's'}"
        )
    if len(s) > max_len:
        raise TextValidationError(
            f"{label} must be at most {max_len} characters"
        )
    if _COLOUR_CODE_RE.search(s):
        raise TextValidationError(f"{label} cannot contain colour codes")
    if _has_disallowed_display_char(s):
        raise TextValidationError(
            f"{label} may only contain {DISPLAY_NAME_HINT}"
        )
    return s


def assert_optional_display_name(
    value: str | None,
    *,
    max_len: int,
    field: str = "name",
) -> str | None:
    """Empty/whitespace → None; otherwise same rules as display name (min 1)."""
    raw = str(value or "").strip()
    if not raw:
        return None
    return assert_display_name(raw, min_len=1, max_len=max_len, field=field)


def assert_prose(
    value: str | None,
    *,
    min_len: int,
    max_len: int,
    field: str = "text",
    allow_newlines: bool = False,
    allow_colour_codes: bool = False,
) -> str:
    """Validate longer free text; reject controls, colour codes (unless allowed), and emoji."""
    s = normalize_user_text(value, collapse_ws=False)
    label = _label(field).capitalize()
    if not s:
        raise TextValidationError(f"{label} is required")
    if not allow_newlines and ("\n" in s or "\r" in s):
        raise TextValidationError(f"{label} cannot contain line breaks")
    if allow_newlines:
        # Normalize newlines; still reject other controls.
        s = s.replace("\r\n", "\n").replace("\r", "\n")
        if _CONTROL_RE.search(s.replace("\n", "")):
            raise TextValidationError(f"{label} contains invalid control characters")
    else:
        if _CONTROL_RE.search(s) or "\n" in s or "\r" in s:
            raise TextValidationError(f"{label} contains invalid control characters")
    if not allow_colour_codes and _COLOUR_CODE_RE.search(s):
        raise TextValidationError(f"{label} cannot contain colour codes")
    if len(s) < min_len:
        raise TextValidationError(
            f"{label} must be at least {min_len} character"
            f"{'' if min_len == 1 else 's'}"
        )
    if len(s) > max_len:
        raise TextValidationError(
            f"{label} must be at most {max_len} characters"
        )
    # Reject emoji / symbols outside letters, numbers, punctuation, separators.
    # When colour codes are allowed, skip characters that are part of §/&/# tokens.
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "\n" and allow_newlines:
            i += 1
            continue
        if allow_colour_codes:
            if ch in ("§", "&") and i + 1 < len(s):
                i += 2
                continue
            if ch == "#" and i + 6 < len(s) and all(
                c in "0123456789abcdefABCDEF" for c in s[i + 1 : i + 7]
            ):
                i += 7
                continue
        cat = unicodedata.category(ch)
        if cat.startswith("L") or cat.startswith("N"):
            i += 1
            continue
        if cat.startswith("P") or cat.startswith("Z"):
            i += 1
            continue
        # Allow a few common marks combining with letters (accents as separate codepoints).
        if cat in ("Mn", "Mc"):
            i += 1
            continue
        raise TextValidationError(
            f"{label} contains characters that are not allowed"
        )
    return s


def _self_test() -> None:
    assert assert_display_name("José O'Brien", min_len=1, max_len=32) == "José O'Brien"
    assert assert_display_name("Anne-Marie", min_len=1, max_len=32) == "Anne-Marie"
    assert assert_display_name("  Iron   Sword  ", min_len=1, max_len=80) == "Iron Sword"
    for bad in ("Bob<script>", "evil§cName", "hi😀", "a/b", "x,y"):
        try:
            assert_display_name(bad, min_len=1, max_len=80)
            raise AssertionError(f"expected reject: {bad!r}")
        except TextValidationError:
            pass
    assert assert_prose("A fine clue here!!", min_len=12, max_len=48).startswith("A fine")
    try:
        assert_prose("short", min_len=12, max_len=48)
        raise AssertionError("expected too short")
    except TextValidationError:
        pass
    try:
        assert_prose("hello §cworld enough", min_len=3, max_len=48)
        raise AssertionError("expected colour reject")
    except TextValidationError:
        pass
    try:
        assert_prose("emoji 😀 in prose text here", min_len=3, max_len=80)
        raise AssertionError("expected emoji reject")
    except TextValidationError:
        pass
    assert assert_optional_display_name("", max_len=24) is None
    assert assert_optional_display_name("Male", max_len=24) == "Male"
    print("text_validation self-test OK")


if __name__ == "__main__":
    _self_test()
