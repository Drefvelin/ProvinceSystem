"""Large bow thin models (parent bow + locked enlarged display)."""

from __future__ import annotations

import copy
from typing import Any

from .constants import load_constants
from .textures import texture_path

# stem → filename suffix after slug (empty for standby texture)
_BOW_SUFFIX = {
    "texture": "",
    "pull_0": "_0",
    "pull_1": "_1",
    "pull_2": "_2",
    "charged": "_charged",
}

BOW_STEMS = ("texture", "pull_0", "pull_1", "pull_2")


def bow_file_suffix(stem: str) -> str:
    if stem not in _BOW_SUFFIX:
        raise ValueError(f"unknown bow stem: {stem}")
    return _BOW_SUFFIX[stem]


def build_large_bow_model(slug: str, stem: str) -> dict[str, Any]:
    consts = load_constants()["large_bow"]
    suffix = bow_file_suffix(stem)
    return {
        "parent": consts["parent"],
        "display": copy.deepcopy(consts["display"]),
        "textures": {"layer0": texture_path(slug + suffix)},
    }


def build_large_bow_models(slug: str) -> dict[str, dict[str, Any]]:
    """Map stem → model dict for standby + pull frames."""
    return {stem: build_large_bow_model(slug, stem) for stem in BOW_STEMS}
