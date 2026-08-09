"""Write fixed-stem PNG/JSON files for skins submissions."""

from __future__ import annotations

import json
import shutil
import struct
from datetime import datetime, timezone
from pathlib import Path

from .db import SKINS_DIR
from .display import DisplayError, model_to_bytes, parse_and_merge_model
from .naming import (
    ARMOR_ICON_FIELDS,
    ARMOR_LAYER_FIELDS,
    BOW_FRAME_FIELDS,
    CROSSBOW_FRAME_FIELDS,
)

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_PNG_BYTES = 2 * 1024 * 1024
MAX_JSON_BYTES = 512 * 1024

ICON_SIZE = (16, 16)
LAYER_SIZE = (64, 32)
ITEM_SIZE = (16, 16)
LARGE_HANDHELD_SIZE = (32, 32)
BOW_SIZE = (16, 16)
LARGE_BOW_SIZE = (32, 32)
CROSSBOW_SIZE = (16, 16)

SINGLE_TEXTURE_KINDS = frozenset({"handheld", "large_handheld"})
BOW_KINDS = frozenset({"bow", "large_bow"})
CROSSBOW_KINDS = frozenset({"crossbow"})
ITEM_KINDS = frozenset(
    {"handheld", "large_handheld", "bow", "large_bow", "crossbow"}
)
MODEL_3D_KINDS = frozenset({"item_3d", "shield", "helmet_3d"})
GUN_KIND = "gun"
GUN_MODEL_FIELDS = ("carry_model", "reload_model", "aim_model")
GUN_MODEL_STEMS = ("carry", "reload", "aim")


class StorageError(ValueError):
    """Invalid upload bytes or kind."""


def png_dimensions(data: bytes) -> tuple[int, int]:
    if len(data) < 24:
        raise StorageError("PNG too short to read dimensions")
    if data[12:16] != b"IHDR":
        raise StorageError("PNG missing IHDR chunk")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def validate_png(
    data: bytes, expected: tuple[int, int] | None = None
) -> None:
    if not data:
        raise StorageError("Empty file")
    if len(data) > MAX_PNG_BYTES:
        raise StorageError(f"PNG exceeds max size ({MAX_PNG_BYTES} bytes)")
    if not data.startswith(PNG_MAGIC):
        raise StorageError("File is not a valid PNG")
    if expected is not None:
        width, height = png_dimensions(data)
        exp_w, exp_h = expected
        if (width, height) != expected:
            raise StorageError(
                f"PNG must be {exp_w}x{exp_h}, got {width}x{height}"
            )


def validate_model_json_size(data: bytes) -> None:
    if not data:
        raise StorageError("Empty model JSON")
    if len(data) > MAX_JSON_BYTES:
        raise StorageError(
            f"Model JSON exceeds max size ({MAX_JSON_BYTES} bytes)"
        )


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _expected_bow_size(kind: str) -> tuple[int, int]:
    if kind == "large_bow":
        return LARGE_BOW_SIZE
    if kind == "crossbow":
        return CROSSBOW_SIZE
    return BOW_SIZE


def _write_bow_frames(
    out_dir: Path,
    slug: str,
    kind: str,
    files: dict[str, bytes],
    fields: tuple[str, ...],
) -> None:
    size = _expected_bow_size(kind)
    for field in fields:
        if field not in files:
            raise StorageError(f"Missing file field: {field}")
        validate_png(files[field], size)
        if field == "texture":
            (out_dir / f"{slug}.png").write_bytes(files[field])
        elif field.startswith("pull_"):
            n = field.split("_", 1)[1]
            (out_dir / f"{slug}_{n}.png").write_bytes(files[field])
        elif field == "charged":
            (out_dir / f"{slug}_charged.png").write_bytes(files[field])
            (out_dir / f"{slug}_arrow.png").write_bytes(files[field])
        else:
            raise StorageError(f"Unknown bow field: {field}")


def _write_model_3d(
    out_dir: Path, slug: str, kind: str, files: dict[str, bytes]
) -> None:
    if "texture" not in files:
        raise StorageError("Missing file field: texture")
    if "model" not in files:
        raise StorageError("Missing file field: model")
    validate_png(files["texture"])
    validate_model_json_size(files["model"])
    try:
        model = parse_and_merge_model(files["model"], kind)
    except DisplayError as e:
        raise StorageError(str(e)) from e
    (out_dir / f"{slug}.png").write_bytes(files["texture"])
    (out_dir / f"{slug}.json").write_bytes(model_to_bytes(model))


def _write_gun(out_dir: Path, slug: str, files: dict[str, bytes]) -> None:
    if "texture" not in files:
        raise StorageError("Missing file field: texture")
    validate_png(files["texture"])
    (out_dir / f"{slug}.png").write_bytes(files["texture"])
    for field, stem in zip(GUN_MODEL_FIELDS, GUN_MODEL_STEMS, strict=True):
        if field not in files:
            raise StorageError(f"Missing file field: {field}")
        validate_model_json_size(files[field])
        try:
            model = parse_and_merge_model(files[field], "gun")
        except DisplayError as e:
            raise StorageError(f"{field}: {e}") from e
        (out_dir / f"{slug}_{stem}.json").write_bytes(model_to_bytes(model))


def _write_armor(
    out_dir: Path,
    files: dict[str, bytes],
    tiers: list[str],
    helmet_3d_tiers: list[str],
) -> None:
    helmet_3d = set(helmet_3d_tiers)
    for tier in tiers:
        for field in ARMOR_LAYER_FIELDS:
            key = f"{tier}_{field}"
            if key not in files:
                raise StorageError(f"Missing file field: {key}")
            validate_png(files[key], LAYER_SIZE)
            (out_dir / f"{tier}_{field}.png").write_bytes(files[key])

        for field in ("chestplate", "leggings", "boots"):
            key = f"{tier}_{field}"
            if key not in files:
                raise StorageError(f"Missing file field: {key}")
            validate_png(files[key], ICON_SIZE)
            (out_dir / f"{tier}_{field}.png").write_bytes(files[key])

        if tier in helmet_3d:
            model_key = f"{tier}_helmet_model"
            tex_key = f"{tier}_helmet_texture"
            if model_key not in files:
                raise StorageError(f"Missing file field: {model_key}")
            if tex_key not in files:
                raise StorageError(f"Missing file field: {tex_key}")
            validate_png(files[tex_key])
            validate_model_json_size(files[model_key])
            try:
                model = parse_and_merge_model(
                    files[model_key], "armor_helmet_3d"
                )
            except DisplayError as e:
                raise StorageError(str(e)) from e
            (out_dir / f"{tier}_helmet_texture.png").write_bytes(
                files[tex_key]
            )
            (out_dir / f"{tier}_helmet_model.json").write_bytes(
                model_to_bytes(model)
            )
        else:
            key = f"{tier}_helmet"
            if key not in files:
                raise StorageError(f"Missing file field: {key}")
            validate_png(files[key], ICON_SIZE)
            (out_dir / f"{tier}_helmet.png").write_bytes(files[key])


def write_submission_files(
    submission_id: str,
    slug: str,
    kind: str,
    display_name: str,
    files: dict[str, bytes],
    grip_preset: str | None = None,
    base_set: str | None = None,
    *,
    tiers: list[str] | None = None,
    helmet_3d_tiers: list[str] | None = None,
    add_name: bool = False,
    name_colours: list[str] | None = None,
    name_styles: list[str] | None = None,
    tier_aliases: dict[str, str] | None = None,
) -> Path:
    """
    Write assets under SKINS_DIR/{submission_id}/ with fixed stems.
    Upload filenames are ignored; `files` keys are logical field names.
    """
    out_dir = SKINS_DIR / submission_id
    out_dir.mkdir(parents=True, exist_ok=True)
    h3d = list(helmet_3d_tiers or [])

    try:
        if kind == "armor_set":
            tier_list = list(tiers or [])
            if not tier_list:
                raise StorageError("armor_set requires at least one tier")
            _write_armor(out_dir, files, tier_list, h3d)
        elif kind in SINGLE_TEXTURE_KINDS:
            if "texture" not in files:
                raise StorageError("Missing file field: texture")
            size = (
                LARGE_HANDHELD_SIZE
                if kind == "large_handheld"
                else ITEM_SIZE
            )
            validate_png(files["texture"], size)
            (out_dir / f"{slug}.png").write_bytes(files["texture"])
        elif kind in BOW_KINDS:
            _write_bow_frames(out_dir, slug, kind, files, BOW_FRAME_FIELDS)
        elif kind in CROSSBOW_KINDS:
            _write_bow_frames(
                out_dir, slug, kind, files, CROSSBOW_FRAME_FIELDS
            )
        elif kind in MODEL_3D_KINDS:
            _write_model_3d(out_dir, slug, kind, files)
        elif kind == GUN_KIND:
            _write_gun(out_dir, slug, files)
        else:
            raise StorageError(f"Unsupported kind: {kind}")

        meta = {
            "id": submission_id,
            "slug": slug,
            "kind": kind,
            "display_name": display_name,
            "grip_preset": grip_preset,
            "base_set": base_set,
            "tiers": list(tiers or []),
            "helmet_3d_tiers": h3d,
            "tier_aliases": dict(tier_aliases or {}),
            "add_name": bool(add_name),
            "name_colours": list(name_colours or []),
            "name_styles": list(name_styles or []),
            "created_at": _iso_now(),
        }
        (out_dir / "meta.json").write_text(
            json.dumps(meta, indent=2) + "\n",
            encoding="utf-8",
        )
    except Exception:
        if out_dir.exists():
            shutil.rmtree(out_dir, ignore_errors=True)
        raise

    return out_dir
