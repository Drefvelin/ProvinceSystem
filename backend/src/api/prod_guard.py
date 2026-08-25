"""Production startup guard for dev bypass flags and missing API keys."""

from __future__ import annotations

import os


def is_production() -> bool:
    return os.environ.get("PS_PRODUCTION", "").strip() == "1"


def assert_production_safe() -> None:
    if not is_production():
        return

    errors: list[str] = []
    if os.environ.get("SKINS_DEV", "").strip() == "1":
        errors.append("SKINS_DEV must not be set when PS_PRODUCTION=1")
    if os.environ.get("CHARACTER_UI_DEV", "").strip() == "1":
        errors.append("CHARACTER_UI_DEV must not be set when PS_PRODUCTION=1")
    if not os.environ.get("PLUGIN_KEY", "").strip():
        errors.append("PLUGIN_KEY is required when PS_PRODUCTION=1")
    if not os.environ.get("STAFF_KEY", "").strip():
        errors.append("STAFF_KEY is required when PS_PRODUCTION=1")
    if errors:
        raise RuntimeError("Production startup refused: " + "; ".join(errors))
