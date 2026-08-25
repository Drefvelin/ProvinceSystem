"""Rewrite model textures.* paths to tfmc_submissions:item/{texture_id}."""

from __future__ import annotations

import copy
import json
from typing import Any

from .constants import namespace


def texture_path(texture_id: str) -> str:
    return f"{namespace()}:item/{texture_id}"


def normalize_textures(model: dict[str, Any], texture_id: str) -> dict[str, Any]:
    """Return a deep copy with every textures.* string rewritten."""
    out = copy.deepcopy(model)
    tex_path = texture_path(texture_id)
    textures = out.get("textures")
    if not isinstance(textures, dict) or len(textures) == 0:
        out["textures"] = {"0": tex_path, "particle": tex_path}
        return out
    for key, value in list(textures.items()):
        if isinstance(value, str):
            textures[key] = tex_path
    out["textures"] = textures
    return out


def model_to_bytes(model: dict[str, Any]) -> bytes:
    return (json.dumps(model, indent=2) + "\n").encode("utf-8")
