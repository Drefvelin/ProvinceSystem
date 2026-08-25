"""Web character creator tier gate (policy from RPCharacters creation catalog)."""

from __future__ import annotations

from typing import Any


def _realm_key(realm_id: str | None) -> str:
    from src.skins.codes import CodeError, normalize_realm_id

    try:
        return normalize_realm_id(realm_id)
    except CodeError:
        return "main"


def _group_display_name(catalog: dict[str, Any], group_id: str) -> str:
    gid = (group_id or "").strip().lower()
    if not gid:
        return ""
    slot_limits = catalog.get("slot_limits")
    if not isinstance(slot_limits, dict):
        return gid
    groups = slot_limits.get("groups")
    if not isinstance(groups, list):
        return gid
    for raw in groups:
        if not isinstance(raw, dict):
            continue
        if str(raw.get("id") or "").strip().lower() == gid:
            display = str(raw.get("display_name") or raw.get("id") or gid).strip()
            return display or gid
    return gid


def realm_policy(catalog: dict[str, Any], realm_id: str | None) -> dict[str, Any]:
    """Minimum tier policy for a realm from catalog.web_creator_access."""
    realm = _realm_key(realm_id)
    access = catalog.get("web_creator_access")
    if not isinstance(access, dict):
        access = {}
    by_realm = access.get("by_realm")
    if not isinstance(by_realm, dict):
        by_realm = {}

    cfg = by_realm.get(realm)
    if not isinstance(cfg, dict):
        cfg = {}

    try:
        min_tier = max(0, int(cfg.get("min_tier", 0)))
    except (TypeError, ValueError):
        min_tier = 0

    min_group_id = str(cfg.get("min_group_id") or "").strip().lower()
    return {
        "realm_id": realm,
        "min_tier": min_tier,
        "min_group_id": min_group_id,
        "min_group_display": _group_display_name(catalog, min_group_id),
    }


def player_donator_tier(entitlements: dict[str, Any]) -> int:
    raw = entitlements.get("donator_tier")
    if raw is None:
        return 0
    try:
        return max(0, int(raw))
    except (TypeError, ValueError):
        return 0


def resolve_gate(
    catalog: dict[str, Any],
    *,
    realm_id: str | None,
    entitlements: dict[str, Any],
) -> dict[str, Any]:
    policy = realm_policy(catalog, realm_id)
    tier = player_donator_tier(entitlements)
    min_tier = int(policy["min_tier"])
    allowed = tier >= min_tier
    return {
        "web_creator_allowed": allowed,
        "web_creator_min_tier": min_tier,
        "web_creator_min_group_id": policy["min_group_id"],
        "web_creator_min_group_display": policy["min_group_display"],
        "donator_tier": tier,
    }


def gate_error_message(gate: dict[str, Any]) -> str:
    min_tier = int(gate.get("web_creator_min_tier") or 0)
    if min_tier <= 0:
        return "web character creator is not available"
    group_id = str(gate.get("web_creator_min_group_id") or "").strip()
    if group_id:
        label = group_id.replace("_", " ").title()
    else:
        label = f"tier {min_tier}"
    return f"web character creator requires {label} rank or higher"
