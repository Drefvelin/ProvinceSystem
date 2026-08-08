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

# Bow / large_bow / crossbow multi-frame (same id prefix on all files)
BOW_PULL_FIELDS = ("pull_0", "pull_1", "pull_2")
BOW_FRAME_FIELDS = ("texture",) + BOW_PULL_FIELDS
CROSSBOW_FRAME_FIELDS = BOW_FRAME_FIELDS + ("charged",)

BOW_SUFFIXES = {
    "texture": ".png",
    "pull_0": "_0.png",
    "pull_1": "_1.png",
    "pull_2": "_2.png",
}
CROSSBOW_SUFFIXES = {
    **BOW_SUFFIXES,
    "charged": "_charged.png",
}

BOW_FIELD_LABELS = {
    "texture": "Standby texture",
    "pull_0": "Pull 0",
    "pull_1": "Pull 1",
    "pull_2": "Pull 2",
    "charged": "Charged",
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


def _slug_from_prefixed_filenames(
    filenames: dict[str, str | None],
    suffixes: dict[str, str],
    labels: dict[str, str],
    kind_label: str,
) -> str:
    """Shared helper: each field `{id}{suffix}` with the same id."""
    resolved: dict[str, str] = {}
    for field, suffix in suffixes.items():
        label = labels[field]
        if field not in filenames or not filenames[field]:
            raise SlugError(f"Missing {label} file.")
        name = _basename(filenames[field])
        if not name.endswith(".png"):
            raise SlugError(
                f"{label} file must be a PNG named like "
                f"`blue_shortbow{suffix}` (got `{name}`)."
            )
        if field == "texture":
            if name.count(".") != 1 or not name.endswith(".png"):
                raise SlugError(
                    f"{label} file must be named exactly `{{id}}.png` "
                    f"(example: `blue_shortbow.png`). Got `{name}`."
                )
            # Reject `{id}_0.png` etc. in the standby slot
            stem = name[: -len(".png")]
            if any(
                stem.endswith(s[: -len(".png")])
                for s in ("_0.png", "_1.png", "_2.png", "_charged.png")
            ):
                raise SlugError(
                    f"{label} file must be the base name `{{id}}.png`, "
                    f"not a pull/charged frame (got `{name}`)."
                )
        elif not name.endswith(suffix):
            raise SlugError(
                f"{label} file must be named exactly "
                f"`{{id}}{suffix}` (example: `blue_shortbow{suffix}`). "
                f"Got `{name}`."
            )
        if field == "texture":
            stem = name[: -len(".png")]
        else:
            stem = name[: -len(suffix)]
        try:
            resolved[field] = assert_slug(stem)
        except SlugError as e:
            raise SlugError(
                f"{label} file `{name}` has an invalid id before `{suffix}`. "
                "Use lowercase letters, numbers, and underscores only "
                f"(example: `blue_shortbow{suffix}`)."
            ) from e

    ids = set(resolved.values())
    if len(ids) != 1:
        parts = ", ".join(
            f"{labels[f]}=`{resolved[f]}`" for f in suffixes
        )
        raise SlugError(
            f"All {kind_label} PNGs must share the same id prefix as the "
            f"base `{{id}}.png` (got different ids: {parts})."
        )
    return next(iter(ids))


def slug_from_bow_filenames(filenames: dict[str, str | None]) -> str:
    """
    Bow / large_bow: `{id}.png`, `{id}_0.png`, `{id}_1.png`, `{id}_2.png`.
    """
    return _slug_from_prefixed_filenames(
        filenames,
        BOW_SUFFIXES,
        BOW_FIELD_LABELS,
        "bow",
    )


def slug_from_crossbow_filenames(filenames: dict[str, str | None]) -> str:
    """
    Crossbow: bow four frames plus `{id}_charged.png`.
    """
    return _slug_from_prefixed_filenames(
        filenames,
        CROSSBOW_SUFFIXES,
        BOW_FIELD_LABELS,
        "crossbow",
    )


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
    elif kind in ("handheld", "large_handheld"):
        derived = slug_from_texture_filename(filenames.get("texture"))
    elif kind in ("bow", "large_bow"):
        derived = slug_from_bow_filenames(filenames)
    elif kind == "crossbow":
        derived = slug_from_crossbow_filenames(filenames)
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
    assert (
        slug_from_bow_filenames(
            {
                "texture": "blue_shortbow.png",
                "pull_0": "blue_shortbow_0.png",
                "pull_1": "blue_shortbow_1.png",
                "pull_2": "blue_shortbow_2.png",
            }
        )
        == "blue_shortbow"
    )
    assert (
        slug_from_crossbow_filenames(
            {
                "texture": "blue_cross.png",
                "pull_0": "blue_cross_0.png",
                "pull_1": "blue_cross_1.png",
                "pull_2": "blue_cross_2.png",
                "charged": "blue_cross_charged.png",
            }
        )
        == "blue_cross"
    )
    try:
        slug_from_bow_filenames(
            {
                "texture": "blue_shortbow.png",
                "pull_0": "red_bow_0.png",
                "pull_1": "blue_shortbow_1.png",
                "pull_2": "blue_shortbow_2.png",
            }
        )
    except SlugError:
        pass
    else:
        raise SystemExit("expected SlugError for mismatched bow ids")

    for bad in ("BlueKnight", "blue-knight", "texture", "1abc", "blue__knight"):
        try:
            assert_slug(bad)
        except SlugError:
            pass
        else:
            raise SystemExit(f"expected SlugError for {bad!r}")

    assert slugify_display_name("Blue Knight") == "blue_knight"
    print("naming ok")
