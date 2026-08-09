"""Render coloured display-name preview PNGs for Discord staff review."""

from __future__ import annotations

import io
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .db import SKINS_DIR

PAD_X = 16
PAD_Y = 12
BG = (26, 26, 26)
DEFAULT_HEX = "#ffffff"
FONT_SIZE = 28
_HEX_RE = re.compile(r"^#?[0-9A-Fa-f]{6}$")

LEGACY_HEX = {
    "0": "#000000",
    "1": "#0000aa",
    "2": "#00aa00",
    "3": "#00aaaa",
    "4": "#aa0000",
    "5": "#aa00aa",
    "6": "#ffaa00",
    "7": "#aaaaaa",
    "8": "#555555",
    "9": "#5555ff",
    "a": "#55ff55",
    "b": "#55ffff",
    "c": "#ff5555",
    "d": "#ff55ff",
    "e": "#ffff55",
    "f": "#ffffff",
}


def _font(size: int = FONT_SIZE) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        try:
            return ImageFont.truetype("DejaVuSans.ttf", size)
        except OSError:
            return ImageFont.load_default()


def _normalize_hex(token: str) -> str | None:
    t = (token or "").strip()
    if not t:
        return None
    if len(t) == 2 and t[0] in ("§", "&", "\u00a7"):
        return LEGACY_HEX.get(t[1].lower())
    if len(t) == 1:
        return LEGACY_HEX.get(t.lower())
    if t.startswith("\u00a7") and len(t) == 2:
        return LEGACY_HEX.get(t[1].lower())
    if not _HEX_RE.match(t):
        return None
    return (t if t.startswith("#") else f"#{t}").lower()


def _parse_rgb(hex_color: str) -> tuple[int, int, int]:
    v = int(hex_color[1:], 16)
    return (v >> 16) & 0xFF, (v >> 8) & 0xFF, v & 0xFF


def _lerp(
    a: tuple[int, int, int], b: tuple[int, int, int], t: float
) -> tuple[int, int, int]:
    c = max(0.0, min(1.0, t))
    return (
        int(round(a[0] + (b[0] - a[0]) * c)),
        int(round(a[1] + (b[1] - a[1]) * c)),
        int(round(a[2] + (b[2] - a[2]) * c)),
    )


def _char_colours(text: str, colour_tokens: list[str] | None) -> list[tuple[str, tuple[int, int, int]]]:
    plain = text or ""
    hexes: list[str] = []
    for tok in colour_tokens or []:
        h = _normalize_hex(str(tok))
        if h:
            hexes.append(h)
    if not plain:
        return []
    if not hexes:
        rgb = _parse_rgb(DEFAULT_HEX)
        return [(ch, rgb) for ch in plain]
    if len(hexes) == 1:
        rgb = _parse_rgb(hexes[0])
        return [(ch, rgb) for ch in plain]
    stops = len(hexes)
    length = len(plain)
    out: list[tuple[str, tuple[int, int, int]]] = []
    for i, ch in enumerate(plain):
        t = 0.0 if length == 1 else i / (length - 1)
        segment = int(t * (stops - 1))
        if segment >= stops - 1:
            segment = stops - 2
        local_t = t * (stops - 1) - segment
        out.append(
            (
                ch,
                _lerp(
                    _parse_rgb(hexes[segment]),
                    _parse_rgb(hexes[segment + 1]),
                    local_t,
                ),
            )
        )
    return out


def render_name_preview_png(
    display_name: str,
    name_colours: list[str] | None = None,
    name_styles: list[str] | None = None,
) -> bytes:
    """Return PNG bytes of the coloured display name on a dark background."""
    text = (display_name or "").strip() or "—"
    styles = {str(s).strip().lower() for s in (name_styles or [])}
    bold = "bold" in styles
    italic = "italic" in styles
    underline = "underline" in styles or "underlined" in styles
    strike = "strikethrough" in styles or "strike" in styles

    font = _font(FONT_SIZE + (2 if bold else 0))
    chars = _char_colours(text, name_colours)

    # Measure with a temp image
    tmp = Image.new("RGB", (1, 1), BG)
    draw = ImageDraw.Draw(tmp)
    widths: list[int] = []
    max_h = 0
    for ch, _rgb in chars:
        bbox = draw.textbbox((0, 0), ch, font=font)
        w = max(1, bbox[2] - bbox[0])
        h = max(1, bbox[3] - bbox[1])
        widths.append(w)
        max_h = max(max_h, h)

    text_w = sum(widths) + max(0, len(widths) - 1)  # 1px letter spacing
    # Italic shear needs a little extra room
    if italic:
        text_w = int(text_w * 1.08) + 4

    width = text_w + PAD_X * 2
    height = max_h + PAD_Y * 2 + (4 if underline or strike else 0)
    canvas = Image.new("RGB", (max(width, 64), max(height, 40)), BG)
    draw = ImageDraw.Draw(canvas)

    x = PAD_X
    baseline_y = PAD_Y
    for (ch, rgb), w in zip(chars, widths):
        if italic:
            # Draw onto a small tile then shear
            tile = Image.new("RGBA", (w + 8, max_h + 8), (0, 0, 0, 0))
            td = ImageDraw.Draw(tile)
            td.text((2, 2), ch, fill=rgb + (255,), font=font)
            shear = 0.25
            sheared = tile.transform(
                tile.size,
                Image.Transform.AFFINE,
                (1, shear, -shear * 4, 0, 1, 0),
                resample=Image.Resampling.BILINEAR,
            )
            canvas.paste(sheared, (x - 2, baseline_y - 2), sheared)
        else:
            if bold:
                for dx, dy in ((0, 0), (1, 0), (0, 1)):
                    draw.text((x + dx, baseline_y + dy), ch, fill=rgb, font=font)
            else:
                draw.text((x, baseline_y), ch, fill=rgb, font=font)
        x += w + 1

    line_y_base = baseline_y + max_h
    if underline:
        draw.line(
            (PAD_X, line_y_base + 1, PAD_X + text_w, line_y_base + 1),
            fill=(220, 220, 220),
            width=2,
        )
    if strike:
        mid = baseline_y + max_h // 2
        draw.line(
            (PAD_X, mid, PAD_X + text_w, mid),
            fill=(220, 220, 220),
            width=2,
        )

    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    return buf.getvalue()


def write_name_preview(
    submission_id: str,
    display_name: str,
    name_colours: list[str] | None = None,
    name_styles: list[str] | None = None,
) -> Path:
    out_dir = SKINS_DIR / submission_id
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "name_preview.png"
    path.write_bytes(
        render_name_preview_png(display_name, name_colours, name_styles)
    )
    return path
