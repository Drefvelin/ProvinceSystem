"""Submission id helpers (IGN + display name) and armor field constants.

Upload filenames are ignored for identity — the API assigns stems.
See Planning/07-naming-conventions.md.
"""

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

ARMOR_TIERS = frozenset(
    {"iron", "steel", "abyssalite", "mythril", "mage", "infantry"}
)

ARMOR_ICON_FIELDS = ("helmet", "chestplate", "leggings", "boots")
ARMOR_LAYER_FIELDS = ("layer_1", "layer_2")
ARMOR_FIELDS = ARMOR_ICON_FIELDS + ARMOR_LAYER_FIELDS

BOW_PULL_FIELDS = ("pull_0", "pull_1", "pull_2")
BOW_FRAME_FIELDS = ("texture",) + BOW_PULL_FIELDS
CROSSBOW_FRAME_FIELDS = BOW_FRAME_FIELDS + ("charged",)


class SlugError(ValueError):
    """Raised when a skin / submission id fails validation."""


def assert_slug(slug: str) -> str:
    """Validate technical id; return unchanged if valid."""
    if not isinstance(slug, str) or slug == "":
        raise SlugError(
            "Id must use lowercase letters, numbers, and underscores."
        )
    if not SLUG_RE.fullmatch(slug):
        raise SlugError(
            "Id must be 2–48 characters, start with a letter, "
            "and use only lowercase a-z, 0-9, and underscores."
        )
    if "__" in slug:
        raise SlugError("Id cannot contain double underscores (__).")
    if slug in RESERVED:
        raise SlugError(f"The id '{slug}' is reserved.")
    return slug


def sanitize_ign(minecraft_name: str | None) -> str:
    """Sanitize Minecraft IGN to slug fragment (a-z0-9_)."""
    s = (minecraft_name or "").lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        s = "player"
    if s[0].isdigit():
        s = f"p_{s}"
    if len(s) > 16:
        s = s[:16].rstrip("_")
    if not s or s[0].isdigit():
        s = "player"
    return s


def slugify_display_name(display_name: str, *, max_len: int = 48) -> str:
    """Slugify item name for use in submission ids."""
    s = (display_name or "").lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        raise SlugError("Item name must include letters or numbers")
    if s[0].isdigit():
        s = f"skin_{s}"
    if len(s) > max_len:
        s = s[:max_len].rstrip("_")
    if not s:
        raise SlugError("Item name is too short after cleaning")
    return s


def build_submission_id(minecraft_name: str | None, display_name: str) -> str:
    """
    `{sanitized_ign}_{slugify(display_name)}` — API id, pack family, delete key.
    """
    ign = sanitize_ign(minecraft_name)
    # Reserve room for ign + underscore within 48 chars
    max_name = max(8, 48 - len(ign) - 1)
    name_part = slugify_display_name(display_name, max_len=max_name)
    full = f"{ign}_{name_part}"
    try:
        return assert_slug(full)
    except SlugError as e:
        raise SlugError(
            "Could not build a valid skin id from your Minecraft name "
            "and item name. Shorten the item name and try again."
        ) from e


def display_slug_from_submission_id(submission_id: str, ign: str | None) -> str:
    """Strip ign_ prefix when present (for conflict matching)."""
    s = (submission_id or "").strip()
    key = sanitize_ign(ign) if ign else ""
    if key:
        prefix = f"{key}_"
        if s.startswith(prefix) and len(s) > len(prefix):
            return s[len(prefix) :]
    return s
