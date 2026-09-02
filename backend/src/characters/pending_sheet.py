"""Build roster-style sheet fields for pending web creates from payload + catalog."""

from __future__ import annotations

import re
from typing import Any

from src.characters.creates import expand_attribute_traits


def _as_dict(raw: Any) -> dict[str, Any]:
    return raw if isinstance(raw, dict) else {}


def _as_list(raw: Any) -> list:
    return raw if isinstance(raw, list) else []


def _catalog_rows_by_id(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for section in ("races", "classes", "traits"):
        for row in _as_list(catalog.get(section)):
            if not isinstance(row, dict):
                continue
            rid = str(row.get("id") or "").strip()
            if rid:
                out[rid] = row
    return out


def _editable_selection_keys(catalog: dict[str, Any]) -> set[str]:
    keys: set[str] = set()
    for stage in _as_list(catalog.get("stages")):
        if not isinstance(stage, dict):
            continue
        if str(stage.get("type") or "").strip().lower() != "selection":
            continue
        if str(stage.get("target") or "").strip().lower() != "trait":
            continue
        key = str(stage.get("key") or "").strip().lower()
        if key:
            keys.add(key)
    return keys


def _attribute_abbreviations(catalog: dict[str, Any]) -> dict[str, str]:
    apb = _as_dict(catalog.get("attribute_point_buy"))
    raw = _as_dict(apb.get("abbreviations"))
    out: dict[str, str] = {}
    for attr, abbr in raw.items():
        a = str(attr or "").strip().lower()
        b = str(abbr or "").strip().lower()
        if a and b:
            out[a] = b
    return out


def _is_attribute_rank_trait(trait_id: str, catalog: dict[str, Any]) -> bool:
    tid = (trait_id or "").strip().lower()
    if not tid:
        return False
    for abbr in _attribute_abbreviations(catalog).values():
        if re.fullmatch(re.escape(abbr) + r"[0-9]+", tid):
            return True
    return False


def _modifier_source_ids(payload: dict[str, Any], catalog: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    race_id = str(payload.get("race_id") or "").strip()
    class_id = str(payload.get("class_id") or "").strip()
    if race_id:
        ids.append(race_id)
    if class_id:
        ids.append(class_id)

    selected = [
        str(t).strip()
        for t in _as_list(payload.get("traits"))
        if str(t).strip()
    ]
    ids.extend(selected)

    attr_traits = _as_list(payload.get("attribute_traits"))
    if attr_traits:
        ids.extend(str(t).strip() for t in attr_traits if str(t).strip())
    else:
        apb = _as_dict(catalog.get("attribute_point_buy"))
        abbreviations = _attribute_abbreviations(catalog)
        pattern = str(apb.get("trait_id_pattern") or "{abbr}{rank}").strip()
        ranks_raw = _as_dict(payload.get("attributes"))
        ranks: dict[str, int] = {}
        for key, val in ranks_raw.items():
            k = str(key or "").strip().lower()
            if not k:
                continue
            try:
                ranks[k] = int(val)
            except (TypeError, ValueError):
                continue
        if ranks:
            ids.extend(expand_attribute_traits(ranks, abbreviations, pattern))

    seen: set[str] = set()
    out: list[str] = []
    for tid in ids:
        if tid in seen:
            continue
        seen.add(tid)
        out.append(tid)
    return out


def _row_attribute_modifiers(row: dict[str, Any]) -> list[dict[str, Any]]:
    raw = row.get("attribute_modifiers")
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        typ = str(item.get("type") or "").strip().lower()
        if not typ:
            continue
        try:
            amount = int(item.get("amount"))
        except (TypeError, ValueError):
            continue
        out.append({"type": typ, "amount": amount})
    return out


def _row_experience_modifiers(row: dict[str, Any]) -> list[dict[str, Any]]:
    raw = row.get("experience_modifiers")
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        profession = str(item.get("profession") or "").strip().lower()
        if not profession:
            continue
        try:
            amount = int(item.get("amount"))
        except (TypeError, ValueError):
            continue
        alias = str(item.get("alias") or "").strip() or profession
        out.append({"profession": profession, "alias": alias, "amount": amount})
    return out


def build_attribute_totals(
    payload: dict[str, Any], catalog: dict[str, Any]
) -> dict[str, int]:
    by_id = _catalog_rows_by_id(catalog)
    totals: dict[str, int] = {}
    for source_id in _modifier_source_ids(payload, catalog):
        row = by_id.get(source_id)
        if not row:
            continue
        for mod in _row_attribute_modifiers(row):
            typ = mod["type"]
            totals[typ] = totals.get(typ, 0) + int(mod["amount"])
    return totals


def build_experience_modifiers(
    payload: dict[str, Any], catalog: dict[str, Any]
) -> list[dict[str, Any]]:
    by_id = _catalog_rows_by_id(catalog)
    merged: dict[str, dict[str, Any]] = {}
    for source_id in _modifier_source_ids(payload, catalog):
        row = by_id.get(source_id)
        if not row:
            continue
        for mod in _row_experience_modifiers(row):
            profession = mod["profession"]
            prev = merged.get(profession)
            merged[profession] = {
                "profession": profession,
                "alias": prev["alias"] if prev else mod["alias"],
                "amount": (prev["amount"] if prev else 0) + int(mod["amount"]),
            }
    return list(merged.values())


def build_sheet_traits(
    payload: dict[str, Any], catalog: dict[str, Any]
) -> list[dict[str, Any]]:
    by_id = _catalog_rows_by_id(catalog)
    editable_keys = _editable_selection_keys(catalog)
    out: list[dict[str, Any]] = []
    for raw_id in _as_list(payload.get("traits")):
        tid = str(raw_id or "").strip()
        if not tid or _is_attribute_rank_trait(tid, catalog):
            continue
        row = by_id.get(tid)
        if not row:
            continue
        key = str(row.get("key") or "").strip().lower()
        if editable_keys and key not in editable_keys:
            continue
        name = str(row.get("name") or tid).strip() or tid
        entry: dict[str, Any] = {"id": tid, "name": name}
        if key:
            entry["key"] = key
        out.append(entry)
    return out


def resolve_display_names(
    payload: dict[str, Any], catalog: dict[str, Any]
) -> tuple[str | None, str | None]:
    by_id = _catalog_rows_by_id(catalog)
    race_name: str | None = None
    class_name: str | None = None
    race_id = str(payload.get("race_id") or "").strip()
    class_id = str(payload.get("class_id") or "").strip()
    if race_id:
        row = by_id.get(race_id)
        if row:
            race_name = str(row.get("name") or "").strip() or None
    if class_id:
        row = by_id.get(class_id)
        if row:
            class_name = str(row.get("name") or "").strip() or None
    return race_name, class_name


def enrich_pending_list_item(
    payload: dict[str, Any], catalog: dict[str, Any]
) -> dict[str, Any]:
    """Sheet overlay for a pending create (attributes, traits, XP, display names)."""
    if not isinstance(payload, dict):
        payload = {}
    out: dict[str, Any] = {}

    attrs = build_attribute_totals(payload, catalog)
    if attrs:
        out["attributes"] = attrs

    xp = build_experience_modifiers(payload, catalog)
    if xp:
        out["experience_modifiers"] = xp

    traits = build_sheet_traits(payload, catalog)
    if traits:
        out["traits"] = traits

    race_name, class_name = resolve_display_names(payload, catalog)
    if race_name:
        out["race_name"] = race_name
    if class_name:
        out["class_name"] = class_name

    return out
