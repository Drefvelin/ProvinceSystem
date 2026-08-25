"""Map registry for public vs staff-only viewer access."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

_CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
_DEFAULT_REGISTRY_PATH = _CONFIG_DIR / "maps.yml"

_registry_cache: dict[str, MapEntry] | None = None


@dataclass(frozen=True)
class MapEntry:
    id: str
    public: bool
    display_name: str
    realm_id: str
    staff_permission: str | None = None

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "display_name": self.display_name,
            "public": self.public,
        }


class MapRegistryError(ValueError):
    """Invalid map registry configuration."""


def _registry_path() -> Path:
    override = os.environ.get("MAP_REGISTRY_PATH", "").strip()
    if override:
        return Path(override)
    return _DEFAULT_REGISTRY_PATH


def _normalize_map_id(map_id: str) -> str | None:
    raw = (map_id or "").strip().lower()
    if not raw or not raw.isalnum():
        return None
    return raw


def _parse_entry(raw: dict[str, Any]) -> MapEntry:
    if not isinstance(raw, dict):
        raise MapRegistryError("Each map entry must be an object")

    map_id = _normalize_map_id(str(raw.get("id") or ""))
    if not map_id:
        raise MapRegistryError("Map entry requires a valid alphanumeric id")

    public = raw.get("public")
    if not isinstance(public, bool):
        raise MapRegistryError(f"Map '{map_id}' requires boolean public")

    display_name = str(raw.get("display_name") or map_id).strip()
    if not display_name:
        display_name = map_id

    realm_raw = raw.get("realm_id")
    realm_id = _normalize_map_id(str(realm_raw)) if realm_raw is not None else map_id
    if not realm_id:
        raise MapRegistryError(f"Map '{map_id}' has invalid realm_id")

    staff_permission = raw.get("staff_permission")
    if staff_permission is not None:
        staff_permission = str(staff_permission).strip() or None

    if not public and not staff_permission:
        raise MapRegistryError(
            f"Map '{map_id}' is not public and requires staff_permission"
        )

    return MapEntry(
        id=map_id,
        public=public,
        display_name=display_name,
        realm_id=realm_id,
        staff_permission=staff_permission,
    )


def load_map_registry(*, force: bool = False) -> dict[str, MapEntry]:
    global _registry_cache

    if _registry_cache is not None and not force:
        return _registry_cache

    path = _registry_path()
    if not path.is_file():
        raise MapRegistryError(f"Map registry not found: {path}")

    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        raise MapRegistryError("Map registry root must be an object")

    raw_maps = data.get("maps")
    if not isinstance(raw_maps, list) or not raw_maps:
        raise MapRegistryError("Map registry requires a non-empty maps list")

    entries: dict[str, MapEntry] = {}
    for item in raw_maps:
        entry = _parse_entry(item)
        if entry.id in entries:
            raise MapRegistryError(f"Duplicate map id '{entry.id}'")
        entries[entry.id] = entry

    _registry_cache = entries
    return entries


def get_map_entry(map_id: str) -> MapEntry | None:
    normalized = _normalize_map_id(map_id)
    if not normalized:
        return None
    return load_map_registry().get(normalized)


def list_map_entries() -> list[MapEntry]:
    return list(load_map_registry().values())


def clear_map_registry_cache() -> None:
    global _registry_cache
    _registry_cache = None
