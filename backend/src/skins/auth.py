"""
Plugin / staff API keys for skins routes.

Local: set SKINS_DEV=1 (see backend/.env.example). Do not commit real secrets.
Headers (for later routes): X-Plugin-Key, X-Staff-Key.
"""

from __future__ import annotations

import logging
import os
import secrets

logger = logging.getLogger("skins.auth")

HEADER_PLUGIN_KEY = "X-Plugin-Key"
HEADER_STAFF_KEY = "X-Staff-Key"
HEADER_SKIN_SESSION = "X-Skin-Session"

_DEV_PLUGIN = "dev-plugin-key"
_DEV_STAFF = "dev-staff-key"

_warned_plugin = False
_warned_staff = False


class AuthError(PermissionError):
    """Missing or invalid plugin/staff key."""


def _skins_dev() -> bool:
    return os.environ.get("SKINS_DEV", "").strip() == "1"


def get_plugin_key() -> str:
    global _warned_plugin
    key = os.environ.get("PLUGIN_KEY", "").strip()
    if key:
        return key
    if _skins_dev():
        if not _warned_plugin:
            logger.warning("PLUGIN_KEY unset; using SKINS_DEV default")
            _warned_plugin = True
        return _DEV_PLUGIN
    raise RuntimeError("PLUGIN_KEY is not set (set SKINS_DEV=1 for local defaults)")


def get_staff_key() -> str:
    global _warned_staff
    key = os.environ.get("STAFF_KEY", "").strip()
    if key:
        return key
    if _skins_dev():
        if not _warned_staff:
            logger.warning("STAFF_KEY unset; using SKINS_DEV default")
            _warned_staff = True
        return _DEV_STAFF
    raise RuntimeError("STAFF_KEY is not set (set SKINS_DEV=1 for local defaults)")


def get_secondary_plugin_keys() -> list[str]:
    """Keys for non-primary servers (dev, tutorial). Comma-separated PLUGIN_KEYS_SECONDARY."""
    raw = os.environ.get("PLUGIN_KEYS_SECONDARY", "")
    return [k.strip() for k in raw.split(",") if k.strip()]


def _key_matches(provided: str, expected: str) -> bool:
    return secrets.compare_digest(provided.encode(), expected.encode())


def is_secondary_plugin_key(provided: str | None) -> bool:
    """True when the caller is a non-primary server.

    Those servers may use every plugin route, but must not replace data the whole site
    shares (creation catalog, kit skins, masked template): the primary server owns it.
    """
    if not provided or _key_matches(provided, get_plugin_key()):
        return False
    return any(_key_matches(provided, k) for k in get_secondary_plugin_keys())


def require_plugin_key(provided: str | None) -> None:
    if not provided:
        raise AuthError("Invalid or missing plugin key")
    if _key_matches(provided, get_plugin_key()) or is_secondary_plugin_key(provided):
        return
    raise AuthError("Invalid or missing plugin key")


def require_staff_key(provided: str | None) -> None:
    expected = get_staff_key()
    if not provided or provided != expected:
        raise AuthError("Invalid or missing staff key")
