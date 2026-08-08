"""Write fixed-stem PNG files for skins submissions."""

from __future__ import annotations

import json
import shutil
import struct
from datetime import datetime, timezone
from pathlib import Path

from .db import SKINS_DIR
from .naming import BOW_FRAME_FIELDS, CROSSBOW_FRAME_FIELDS

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_PNG_BYTES = 2 * 1024 * 1024
ARMOR_ICON_FIELDS = ("helmet", "chestplate", "leggings", "boots")
ARMOR_LAYER_FIELDS = ("layer_1", "layer_2")
ARMOR_FIELDS = ARMOR_ICON_FIELDS + ARMOR_LAYER_FIELDS

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
ITEM_KINDS = SINGLE_TEXTURE_KINDS | BOW_KINDS | CROSSBOW_KINDS
TEXTURE_KINDS = ITEM_KINDS


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
            # ItemsAdder generate:true CROSSBOW often expects *_arrow for charged
            (out_dir / f"{slug}_arrow.png").write_bytes(files[field])
        else:
            raise StorageError(f"Unknown bow field: {field}")


def write_submission_files(
    submission_id: str,
    slug: str,
    kind: str,
    display_name: str,
    files: dict[str, bytes],
    grip_preset: str | None = None,
    base_set: str | None = None,
) -> Path:
    """
    Write PNGs under SKINS_DIR/{submission_id}/ with fixed stems.
    `files` keys: armor fields, `texture` for handheld, or bow frame fields.
    """
    out_dir = SKINS_DIR / submission_id
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        if kind == "armor_set":
            for field in ARMOR_ICON_FIELDS:
                if field not in files:
                    raise StorageError(f"Missing file field: {field}")
                validate_png(files[field], ICON_SIZE)
                (out_dir / f"{slug}_{field}.png").write_bytes(files[field])
            for field in ARMOR_LAYER_FIELDS:
                if field not in files:
                    raise StorageError(f"Missing file field: {field}")
                validate_png(files[field], LAYER_SIZE)
                (out_dir / f"{slug}_{field}.png").write_bytes(files[field])
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
        else:
            raise StorageError(f"Unsupported kind: {kind}")

        meta = {
            "id": submission_id,
            "slug": slug,
            "kind": kind,
            "display_name": display_name,
            "grip_preset": grip_preset,
            "base_set": base_set,
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
