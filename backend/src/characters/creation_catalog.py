"""RPCharacters creation catalog snapshot for the website wizard."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


class CreationCatalogError(ValueError):
    """Invalid creation catalog payload."""


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _as_list(raw: Any, field: str) -> list:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise CreationCatalogError(f"{field} must be a list")
    return raw


def _as_dict(raw: Any, field: str) -> dict[str, Any]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise CreationCatalogError(f"{field} must be an object")
    return raw


def _normalize_stages(raw: list) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i, row in enumerate(raw):
        if not isinstance(row, dict):
            raise CreationCatalogError(f"stages[{i}] must be an object")
        sid = str(row.get("id") or "").strip()
        stype = str(row.get("type") or "").strip().lower()
        if not sid:
            raise CreationCatalogError(f"stages[{i}].id is required")
        if not stype:
            raise CreationCatalogError(f"stages[{i}].type is required")
        entry: dict[str, Any] = {
            "id": sid,
            "type": stype,
            "order": int(row.get("order", i)),
        }
        for key in (
            "target",
            "key",
            "lock_time",
            "repeat",
            "auto_next",
            "min_select",
            "max_select",
            "points",
            "max_rank",
            "messages",
            "dependency",
            "entries",
            "interval",
        ):
            if key in row and row[key] is not None:
                entry[key] = row[key]
        out.append(entry)
    return out


def _normalize_attribute_point_buy(raw: Any) -> dict[str, Any]:
    data = _as_dict(raw, "attribute_point_buy")
    if not data:
        raise CreationCatalogError("attribute_point_buy is required")
    attrs = data.get("attributes")
    if not isinstance(attrs, list) or not attrs:
        raise CreationCatalogError("attribute_point_buy.attributes must be a non-empty list")
    cost = data.get("cost_for_rank")
    if not isinstance(cost, list) or not cost:
        raise CreationCatalogError(
            "attribute_point_buy.cost_for_rank must be a non-empty list"
        )
    try:
        pool = int(data.get("pool"))
        max_rank = int(data.get("max_rank"))
    except (TypeError, ValueError) as e:
        raise CreationCatalogError(
            "attribute_point_buy.pool and max_rank must be integers"
        ) from e
    attributes = [str(a).strip().lower() for a in attrs if str(a or "").strip()]
    cost_for_rank = []
    for c in cost:
        try:
            cost_for_rank.append(int(c))
        except (TypeError, ValueError) as e:
            raise CreationCatalogError(
                "attribute_point_buy.cost_for_rank must be integers"
            ) from e
    abbreviations = data.get("abbreviations")
    if abbreviations is None:
        abbreviations = {}
    if not isinstance(abbreviations, dict):
        raise CreationCatalogError("attribute_point_buy.abbreviations must be an object")
    abbr_out = {
        str(k).strip().lower(): str(v).strip().lower()
        for k, v in abbreviations.items()
        if str(k or "").strip() and str(v or "").strip()
    }
    return {
        "pool": pool,
        "max_rank": max_rank,
        "cost_for_rank": cost_for_rank,
        "attributes": attributes,
        "abbreviations": abbr_out,
        "trait_id_pattern": str(
            data.get("trait_id_pattern") or "{abbr}{rank}"
        ).strip(),
    }


def _normalize_id_rows(raw: list, field: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i, row in enumerate(raw):
        if not isinstance(row, dict):
            raise CreationCatalogError(f"{field}[{i}] must be an object")
        rid = str(row.get("id") or "").strip()
        if not rid:
            raise CreationCatalogError(f"{field}[{i}].id is required")
        entry = dict(row)
        entry["id"] = rid
        out.append(entry)
    return out


def _normalize_payload(raw: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise CreationCatalogError("body must be a JSON object")

    stages = _normalize_stages(_as_list(raw.get("stages"), "stages"))
    attribute_point_buy = _normalize_attribute_point_buy(raw.get("attribute_point_buy"))
    races = _normalize_id_rows(_as_list(raw.get("races"), "races"), "races")
    traits = _normalize_id_rows(_as_list(raw.get("traits"), "traits"), "traits")
    classes = _normalize_id_rows(_as_list(raw.get("classes"), "classes"), "classes")
    validation = _as_dict(raw.get("validation"), "validation")
    slot_limits = _as_dict(raw.get("slot_limits"), "slot_limits")

    return {
        "stages": stages,
        "attribute_point_buy": attribute_point_buy,
        "races": races,
        "traits": traits,
        "classes": classes,
        "validation": validation,
        "slot_limits": slot_limits,
    }


def replace_catalog(raw: dict[str, Any]) -> dict[str, Any]:
    """Full-replace creation catalog snapshot."""
    from src.skins.db import connect

    payload = _normalize_payload(raw)
    updated_at = _iso_now()
    body = json.dumps(payload, separators=(",", ":"))

    with connect() as conn:
        conn.execute(
            """
            INSERT INTO creation_catalog (id, payload, updated_at)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                payload = excluded.payload,
                updated_at = excluded.updated_at
            """,
            (body, updated_at),
        )
        conn.commit()

    return {
        **payload,
        "updated_at": updated_at,
        "stages_count": len(payload["stages"]),
        "races_count": len(payload["races"]),
        "traits_count": len(payload["traits"]),
        "classes_count": len(payload["classes"]),
    }


def _empty_catalog() -> dict[str, Any]:
    return {
        "stages": [],
        "attribute_point_buy": None,
        "races": [],
        "traits": [],
        "classes": [],
        "validation": {},
        "slot_limits": {},
        "updated_at": None,
    }


def get_catalog() -> dict[str, Any]:
    """Return stored snapshot or empty catalog."""
    from src.skins.db import connect

    with connect() as conn:
        row = conn.execute(
            "SELECT payload, updated_at FROM creation_catalog WHERE id = 1"
        ).fetchone()

    if row is None:
        return _empty_catalog()

    try:
        data = json.loads(row["payload"] or "{}")
    except json.JSONDecodeError:
        data = {}
    if not isinstance(data, dict):
        data = {}

    out = _empty_catalog()
    out["updated_at"] = row["updated_at"]
    for key in (
        "stages",
        "races",
        "traits",
        "classes",
        "validation",
        "slot_limits",
        "attribute_point_buy",
    ):
        if key in data:
            out[key] = data[key]
    return out


def require_synced_creation_catalog() -> dict[str, Any]:
    """Return catalog or raise if RPCharacters has not pushed yet."""
    catalog = get_catalog()
    stages = catalog.get("stages") or []
    if not stages or catalog.get("updated_at") is None:
        raise CreationCatalogError("creation catalog not synced")
    if not catalog.get("attribute_point_buy"):
        raise CreationCatalogError("creation catalog missing attribute_point_buy")
    return catalog
