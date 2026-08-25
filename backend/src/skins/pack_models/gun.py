"""Gun model normalize + aim_charged copy."""

from __future__ import annotations

from typing import Any

from .textures import normalize_textures

MODEL_STEMS = ("carry", "reload", "aim")


def build_gun_models(
    models: dict[str, dict[str, Any]], slug: str
) -> dict[str, dict[str, Any]]:
    """
    models keys: carry, reload, aim (display-merged donor dicts).
    Returns carry/reload/aim normalized + aim_charged (copy of aim).
    Texture id for all is the shared slug PNG.
    """
    out: dict[str, dict[str, Any]] = {}
    for stem in MODEL_STEMS:
        if stem not in models:
            raise ValueError(f"missing gun model stem: {stem}")
        out[stem] = normalize_textures(models[stem], slug)
    out["aim_charged"] = normalize_textures(models["aim"], slug)
    return out
