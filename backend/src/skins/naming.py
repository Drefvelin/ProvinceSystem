"""Skin id (slug) validation and filename convention helpers.

See Planning/07-naming-conventions.md. Prefer player-facing errors (avoid “slug”).
"""

from __future__ import annotations

import re
from pathlib import PurePosixPath

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

ARMOR_SUFFIXES = {
    "helmet": "_helmet.png",
    "chestplate": "_chestplate.png",
    "leggings": "_leggings.png",
    "boots": "_boots.png",
    "layer_1": "_layer_1.png",
    "layer_2": "_layer_2.png",
}

ARMOR_FIELD_LABELS = {
    "helmet": "Helmet",
    "chestplate": "Chestplate",
    "leggings": "Leggings",
    "boots": "Boots",
    "layer_1": "Layer 1",
    "layer_2": "Layer 2",
}


class SlugError(ValueError):
    """Raised when a skin id / filename convention fails."""


def assert_slug(slug: str) -> str:
    """Validate technical skin id; return it unchanged if valid."""
    if not isinstance(slug, str) or slug == "":
        raise SlugError(
            "Skin file name must use a valid id (lowercase letters, numbers, underscores)."
        )
    if not SLUG_RE.fullmatch(slug):
        raise SlugError(
            "Skin file name id must be 2–48 characters, start with a letter, "
            "and use only lowercase a-z, 0-9, and underscores "
            "(no spaces, capitals, or hyphens). Example: blue_knight.png"
        )
    if "__" in slug:
        raise SlugError(
            "Skin file name id cannot contain double underscores (__)."
        )
    if slug in RESERVED:
        raise SlugError(
            f"The name '{slug}' is reserved. Rename your PNG (and matching JSON later)."
        )
    return slug


def slugify_display_name(display_name: str) -> str:
    """Suggest a skin id from an item name (tests / helpers only)."""
    s = (display_name or "").lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    if not s or s[0].isdigit():
        s = f"skin_{s}" if s else "skin"
    if len(s) > 48:
        s = s[:48].rstrip("_")
    return assert_slug(s)


def _basename(filename: str | None) -> str:
    if not filename or not str(filename).strip():
        raise SlugError("Each upload must include a file name.")
    # Clients may send paths; take final component only
    name = PurePosixPath(str(filename).replace("\\", "/")).name
    if not name or name in (".", ".."):
        raise SlugError("Each upload must include a file name.")
    return name


def slug_from_texture_filename(filename: str | None) -> str:
    """
    Single texture upload must be named `{id}.png`.
    Returns the skin id.
    """
    name = _basename(filename)
    if not name.endswith(".png"):
        raise SlugError(
            "Texture must be a PNG named like `blue_knight.png` "
            "(lowercase letters, numbers, underscores)."
        )
    stem = name[: -len(".png")]
    try:
        return assert_slug(stem)
    except SlugError as e:
        raise SlugError(
            f"Texture file `{name}` is invalid. "
            "Use a name like `blue_knight.png` "
            "(lowercase letters, numbers, underscores only)."
        ) from e


def slug_from_armor_filenames(filenames: dict[str, str | None]) -> str:
    """
    Armor uploads must be `{id}_helmet.png`, … with the same id on all six.
    `filenames` maps field -> original filename.
    """
    resolved: dict[str, str] = {}
    for field, suffix in ARMOR_SUFFIXES.items():
        label = ARMOR_FIELD_LABELS[field]
        if field not in filenames or not filenames[field]:
            raise SlugError(f"Missing {label} file.")
        name = _basename(filenames[field])
        if not name.endswith(".png"):
            raise SlugError(
                f"{label} file must be a PNG named like "
                f"`blue_knight{suffix}` (got `{name}`)."
            )
        if not name.endswith(suffix):
            raise SlugError(
                f"{label} file must be named exactly "
                f"`{{id}}{suffix}` (example: `blue_knight{suffix}`). "
                f"Got `{name}`."
            )
        stem = name[: -len(suffix)]
        try:
            resolved[field] = assert_slug(stem)
        except SlugError as e:
            raise SlugError(
                f"{label} file `{name}` has an invalid id before `{suffix}`. "
                "Use lowercase letters, numbers, and underscores only "
                f"(example: `blue_knight{suffix}`)."
            ) from e

    ids = set(resolved.values())
    if len(ids) != 1:
        parts = ", ".join(
            f"{ARMOR_FIELD_LABELS[f]}=`{resolved[f]}`" for f in ARMOR_SUFFIXES
        )
        raise SlugError(
            "All armor PNGs must share the same id prefix "
            f"(got different ids: {parts})."
        )
    return next(iter(ids))


def resolve_submission_slug(
    kind: str,
    filenames: dict[str, str | None],
    provided_slug: str | None = None,
) -> str:
    """
    Derive skin id from upload names. If `provided_slug` is set, it must match.
    """
    kind = (kind or "").strip()
    if kind == "armor_set":
        derived = slug_from_armor_filenames(filenames)
    elif kind in ("item", "handheld", "large_handheld"):
        derived = slug_from_texture_filename(filenames.get("texture"))
    else:
        raise SlugError("Unknown submission kind.")

    provided = (provided_slug or "").strip() or None
    if provided is not None:
        provided = assert_slug(provided)
        if provided != derived:
            raise SlugError(
                f"File name id `{derived}` does not match provided id `{provided}`."
            )
    return derived


if __name__ == "__main__":
    assert assert_slug("blue_knight") == "blue_knight"
    assert slug_from_texture_filename("blue_knight.png") == "blue_knight"
    assert (
        slug_from_armor_filenames(
            {
                "helmet": "blue_knight_helmet.png",
                "chestplate": "blue_knight_chestplate.png",
                "leggings": "blue_knight_leggings.png",
                "boots": "blue_knight_boots.png",
                "layer_1": "blue_knight_layer_1.png",
                "layer_2": "blue_knight_layer_2.png",
            }
        )
        == "blue_knight"
    )

    for bad in ("BlueKnight", "blue-knight", "texture", "1abc", "blue__knight"):
        try:
            assert_slug(bad)
        except SlugError:
            pass
        else:
            raise SystemExit(f"expected SlugError for {bad!r}")

    assert slugify_display_name("Blue Knight") == "blue_knight"
    print("naming ok")
