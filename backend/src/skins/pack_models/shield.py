"""Shield idle (overrides) + blocking clone with round idle→blocking Δ."""

from __future__ import annotations

import copy
from typing import Any

from .constants import load_constants, namespace
from .textures import normalize_textures

_ZERO = [0.0, 0.0, 0.0]
_ONE = [1.0, 1.0, 1.0]

HAND_TABS = (
    "thirdperson_righthand",
    "thirdperson_lefthand",
    "firstperson_righthand",
    "firstperson_lefthand",
)


def _as_vec3(value: Any, fallback: list[float]) -> list[float]:
    if not isinstance(value, list) or len(value) < 3:
        return list(fallback)
    out: list[float] = []
    for i in range(3):
        try:
            out.append(float(value[i]))
        except (TypeError, ValueError):
            return list(fallback)
    return out


def _add_vec3(a: list[float], b: list[float]) -> list[float]:
    return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]


def apply_blocking_overrides(idle: dict[str, Any], slug: str) -> None:
    idle["overrides"] = [
        {
            "predicate": {"blocking": 1},
            "model": f"{namespace()}:item/{slug}_blocking",
        }
    ]


def apply_blocking_display_from_idle_delta(model: dict[str, Any]) -> None:
    """Mutate model display: hand tabs = idle + round Δ (scale from idle)."""
    consts = load_constants()["shield"]
    round_idle: dict[str, Any] = consts["round_idle"]
    deltas: dict[str, Any] = consts["round_blocking_delta"]

    display = model.get("display")
    if not isinstance(display, dict):
        display = {}
    else:
        display = copy.deepcopy(display)

    for tab_name in HAND_TABS:
        delta = deltas[tab_name]
        ref = round_idle[tab_name]
        raw_tab = display.get(tab_name)
        if isinstance(raw_tab, dict):
            rotation = _as_vec3(raw_tab.get("rotation"), _ZERO)
            translation = _as_vec3(raw_tab.get("translation"), _ZERO)
            scale = _as_vec3(raw_tab.get("scale"), _ONE)
        else:
            rotation = _as_vec3(ref.get("rotation"), _ZERO)
            translation = _as_vec3(ref.get("translation"), _ZERO)
            scale = _as_vec3(ref.get("scale"), _ONE)

        display[tab_name] = {
            "rotation": _add_vec3(rotation, _as_vec3(delta.get("rotation"), _ZERO)),
            "translation": _add_vec3(
                translation, _as_vec3(delta.get("translation"), _ZERO)
            ),
            "scale": scale,
        }

    model["display"] = display


def build_shield_models(
    idle_model: dict[str, Any], slug: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Return (idle_with_overrides, blocking) ready to write.
    Idle textures normalized to item/{slug}.
    """
    idle = normalize_textures(idle_model, slug)
    apply_blocking_overrides(idle, slug)

    blocking = normalize_textures(idle_model, slug)
    apply_blocking_display_from_idle_delta(blocking)
    blocking.pop("overrides", None)

    return idle, blocking
