"""Slug validation for skins submissions (see Planning/07-naming-conventions.md)."""

from __future__ import annotations

import re

SLUG_RE = re.compile(r"^[a-z][a-z0-9_]{1,47}$")

RESERVED = frozenset(
    {
        "test",
        "texture",
        "null",
        "undefined",
        "admin",
        "tfmc",
    }
)


class SlugError(ValueError):
    """Raised when a slug fails naming rules."""


def assert_slug(slug: str) -> str:
    """Validate a technical slug; return it unchanged if valid."""
    if not isinstance(slug, str) or slug == "":
        raise SlugError("Slug is required (lowercase letters, numbers, underscores).")
    if not SLUG_RE.fullmatch(slug):
        raise SlugError(
            "Slug must be 2–48 characters, start with a letter, "
            "and use only lowercase a-z, 0-9, and underscores "
            "(no spaces, capitals, or hyphens). Example: blue_knight"
        )
    if "__" in slug:
        raise SlugError("Slug cannot contain double underscores (__).")
    if slug in RESERVED:
        raise SlugError(f"Slug '{slug}' is reserved. Choose another name.")
    return slug


def slugify_display_name(display_name: str) -> str:
    """Suggest a slug from a display name, then validate with assert_slug."""
    s = (display_name or "").lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    if not s or s[0].isdigit():
        s = f"skin_{s}" if s else "skin"
    if len(s) > 48:
        s = s[:48].rstrip("_")
    return assert_slug(s)


if __name__ == "__main__":
    assert assert_slug("blue_knight") == "blue_knight"

    for bad in ("BlueKnight", "blue-knight", "texture", "1abc", "blue__knight"):
        try:
            assert_slug(bad)
        except SlugError:
            pass
        else:
            raise SystemExit(f"expected SlugError for {bad!r}")

    assert slugify_display_name("Blue Knight") == "blue_knight"
    print("naming ok")
