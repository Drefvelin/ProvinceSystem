"""Compose staff review contact-sheet PNGs for 2D submissions."""

from __future__ import annotations

import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .db import SKINS_DIR, connect
from .storage import ARMOR_FIELDS, ITEM_KINDS

TILE_DISPLAY = 96
PAD = 12
LABEL_H = 18
BG = (32, 32, 36)
LABEL_COLOR = (220, 220, 220)
CAPTION_COLOR = (200, 200, 210)


class ReviewSheetError(ValueError):
    """Could not build sheet for an existing submission."""


def _font(size: int = 14) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        try:
            return ImageFont.truetype("DejaVuSans.ttf", size)
        except OSError:
            return ImageFont.load_default()


def _load_rgba(path: Path) -> Image.Image:
    try:
        img = Image.open(path)
        img.load()
        return img.convert("RGBA")
    except OSError as e:
        raise ReviewSheetError(f"Cannot read image: {path.name}") from e


def _scale_nn(img: Image.Image, max_side: int) -> Image.Image:
    w, h = img.size
    if w <= 0 or h <= 0:
        return img
    scale = max_side / max(w, h)
    nw = max(1, int(round(w * scale)))
    nh = max(1, int(round(h * scale)))
    return img.resize((nw, nh), Image.Resampling.NEAREST)


def _paste_centered(
    canvas: Image.Image, tile: Image.Image, box: tuple[int, int, int, int]
) -> None:
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    tw, th = tile.size
    px = x0 + (bw - tw) // 2
    py = y0 + (bh - th) // 2
    canvas.paste(tile, (px, py), tile if tile.mode == "RGBA" else None)


def _armor_sheet(slug: str, out_dir: Path) -> bytes:
    cols, rows = 3, 2
    cell_w = TILE_DISPLAY + PAD * 2
    cell_h = TILE_DISPLAY + LABEL_H + PAD * 2
    width = cols * cell_w
    height = rows * cell_h
    canvas = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(canvas)
    font = _font(12)

    for i, field in enumerate(ARMOR_FIELDS):
        path = out_dir / f"{slug}_{field}.png"
        if not path.is_file():
            raise ReviewSheetError(f"Missing file: {path.name}")
        col, row = i % cols, i // cols
        x0 = col * cell_w + PAD
        y0 = row * cell_h + PAD
        tile = _scale_nn(_load_rgba(path), TILE_DISPLAY)
        _paste_centered(
            canvas, tile, (x0, y0, x0 + TILE_DISPLAY, y0 + TILE_DISPLAY)
        )
        label = field
        bbox = draw.textbbox((0, 0), label, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(
            (x0 + (TILE_DISPLAY - tw) // 2, y0 + TILE_DISPLAY + 2),
            label,
            fill=LABEL_COLOR,
            font=font,
        )

    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    return buf.getvalue()


def _item_sheet(
    slug: str,
    kind: str,
    grip_preset: str | None,
    base_set: str | None,
    out_dir: Path,
) -> bytes:
    path = out_dir / f"{slug}.png"
    if not path.is_file():
        raise ReviewSheetError(f"Missing file: {path.name}")

    display = 192
    caption = f"kind={kind}"
    if base_set:
        caption += f"  base={base_set}"
    if grip_preset:
        caption += f"  grip={grip_preset}"

    font = _font(16)
    draw_tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    cb = draw_tmp.textbbox((0, 0), caption, font=font)
    caption_w = cb[2] - cb[0]
    caption_h = cb[3] - cb[1]

    width = max(display + PAD * 2, caption_w + PAD * 2)
    height = display + PAD * 3 + caption_h
    canvas = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(canvas)

    tile = _scale_nn(_load_rgba(path), display)
    _paste_centered(
        canvas,
        tile,
        (PAD, PAD, width - PAD, PAD + display),
    )
    draw.text(
        ((width - caption_w) // 2, PAD + display + PAD),
        caption,
        fill=CAPTION_COLOR,
        font=font,
    )

    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    return buf.getvalue()


def build_review_sheet(submission_id: str) -> bytes | None:
    """
    Build a contact-sheet PNG for staff review.
    Returns None if the submission row does not exist.
    Raises ReviewSheetError if expected files are missing/unreadable.
    """
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM submissions WHERE id = ?",
            (submission_id,),
        ).fetchone()
    if row is None:
        return None

    kind = row["kind"]
    slug = row["slug"]
    grip = row["grip_preset"]
    base_set = row["base_set"] if "base_set" in row.keys() else None
    out_dir = SKINS_DIR / submission_id
    if not out_dir.is_dir():
        raise ReviewSheetError("Submission files directory missing")

    if kind == "armor_set":
        return _armor_sheet(slug, out_dir)
    if kind in ITEM_KINDS:
        return _item_sheet(slug, kind, grip, base_set, out_dir)
    raise ReviewSheetError(f"Unsupported kind for review sheet: {kind}")
