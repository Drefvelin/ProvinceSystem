"""Web character create requests + validation against creation catalog."""

from __future__ import annotations

import json
import uuid as uuid_lib
from datetime import datetime, timezone
from typing import Any

from src.characters.creation_catalog import (
    CreationCatalogError,
    require_synced_creation_catalog,
)
from src.characters.roster import count_alive, get_max_alive


class CreateError(ValueError):
    """Invalid create payload or business rule failure."""


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _as_dict(raw: Any, field: str) -> dict[str, Any]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise CreateError(f"{field} must be an object")
    return raw


def _as_list(raw: Any, field: str) -> list:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise CreateError(f"{field} must be a list")
    return raw


def _nested_int(section: dict, *keys: str, default: int | None = None) -> int | None:
    cur: Any = section
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    try:
        return int(cur)
    except (TypeError, ValueError):
        return default


def _trait_id_for_rank(abbr: str, rank: int, pattern: str) -> str:
    """Build attribute trait id; default pattern {abbr}{rank} → str1."""
    text = (pattern or "{abbr}{rank}").strip()
    return (
        text.replace("{abbr}", abbr)
        .replace("{rank}", str(rank))
        .replace("{ABBR}", abbr.upper())
    )


def attribute_spend(ranks: dict[str, int], cost_for_rank: list[int]) -> int:
    total = 0
    for rank in ranks.values():
        for i in range(int(rank)):
            if i >= len(cost_for_rank):
                raise CreateError("attribute rank exceeds cost_for_rank length")
            total += int(cost_for_rank[i])
    return total


def expand_attribute_traits(
    ranks: dict[str, int],
    abbreviations: dict[str, str],
    pattern: str,
) -> list[str]:
    out: list[str] = []
    for attr, rank in ranks.items():
        abbr = abbreviations.get(attr) or abbreviations.get(attr.lower())
        if not abbr:
            # fallback: first 3 letters
            abbr = attr[:3].lower()
        for r in range(1, int(rank) + 1):
            out.append(_trait_id_for_rank(str(abbr).lower(), r, pattern))
    return out


def _validate_and_normalize(player_uuid: str, body: dict[str, Any]) -> dict[str, Any]:
    catalog = require_synced_creation_catalog()
    validation = _as_dict(catalog.get("validation"), "validation")
    apb = _as_dict(catalog.get("attribute_point_buy"), "attribute_point_buy")
    slot_limits = _as_dict(catalog.get("slot_limits"), "slot_limits")

    name = str(body.get("name") or "").strip()
    name_min = _nested_int(validation, "name", "min_length", default=1) or 1
    name_max = _nested_int(validation, "name", "max_length", default=32) or 32
    if len(name) < name_min or len(name) > name_max:
        raise CreateError(f"name length must be between {name_min} and {name_max}")

    try:
        age = int(body.get("age"))
    except (TypeError, ValueError) as e:
        raise CreateError("age must be an integer") from e
    age_min = _nested_int(validation, "age", "minimum", default=1) or 1
    if age < age_min:
        raise CreateError(f"age must be at least {age_min}")

    description = str(body.get("description") or "").strip()
    desc_min = _nested_int(validation, "description", "min_length", default=1) or 1
    desc_max = _nested_int(validation, "description", "max_length", default=2000) or 2000
    if len(description) < desc_min or len(description) > desc_max:
        raise CreateError(
            f"description length must be between {desc_min} and {desc_max}"
        )

    gender = str(body.get("gender") or "").strip()

    race_id = str(body.get("race_id") or "").strip()
    class_id = str(body.get("class_id") or "").strip()
    race_ids = {
        str(r.get("id") or "").strip()
        for r in (catalog.get("races") or [])
        if isinstance(r, dict)
    }
    class_ids = {
        str(c.get("id") or "").strip()
        for c in (catalog.get("classes") or [])
        if isinstance(c, dict)
    }
    if not race_id or race_id not in race_ids:
        raise CreateError("race_id is invalid")
    if not class_id or class_id not in class_ids:
        raise CreateError("class_id is invalid")

    traits_by_id: dict[str, dict] = {}
    for t in catalog.get("traits") or []:
        if isinstance(t, dict):
            tid = str(t.get("id") or "").strip()
            if tid:
                traits_by_id[tid] = t

    selected_traits = [
        str(t).strip() for t in _as_list(body.get("traits"), "traits") if str(t).strip()
    ]
    for tid in selected_traits:
        if tid not in traits_by_id:
            raise CreateError(f"unknown trait: {tid}")

    # Selection stages: enforce min/max per trait key
    for stage in catalog.get("stages") or []:
        if not isinstance(stage, dict):
            continue
        if str(stage.get("type") or "").lower() != "selection":
            continue
        target = str(stage.get("target") or "").lower()
        key = str(stage.get("key") or "").strip().lower()
        if target != "trait" or not key:
            continue
        min_select = int(stage.get("min_select") or 0)
        max_select = int(stage.get("max_select") or 99)
        count = 0
        for tid in selected_traits:
            tkey = str(traits_by_id[tid].get("key") or "").strip().lower()
            if tkey == key:
                count += 1
        if count < min_select or count > max_select:
            raise CreateError(
                f"traits for key '{key}' must be between {min_select} and {max_select}"
            )

    clues_raw = _as_list(body.get("clues"), "clues")
    clues = [str(c).strip() for c in clues_raw if str(c).strip()]
    clue_cfg = _as_dict(validation.get("clues"), "validation.clues")
    clue_min_len = int(clue_cfg.get("min_length") or 1)
    clue_max_len = int(clue_cfg.get("max_length") or 500)
    max_clues = int(clue_cfg.get("max_clues") or 20)
    required = int(clue_cfg.get("default_required") or 0)
    if len(clues) > max_clues:
        raise CreateError(f"at most {max_clues} clues allowed")
    if len(clues) < required:
        raise CreateError(f"at least {required} clues required")
    for i, clue in enumerate(clues):
        if len(clue) < clue_min_len or len(clue) > clue_max_len:
            raise CreateError(
                f"clues[{i}] length must be between {clue_min_len} and {clue_max_len}"
            )

    attrs_cfg = [str(a).strip().lower() for a in (apb.get("attributes") or [])]
    if not attrs_cfg:
        raise CreateError("catalog attribute_point_buy.attributes is empty")
    cost_for_rank = [int(c) for c in (apb.get("cost_for_rank") or [])]
    pool = int(apb.get("pool"))
    max_rank = int(apb.get("max_rank"))
    abbreviations = {
        str(k).strip().lower(): str(v).strip().lower()
        for k, v in _as_dict(apb.get("abbreviations"), "abbreviations").items()
    }
    pattern = str(apb.get("trait_id_pattern") or "{abbr}{rank}").strip()

    raw_attrs = _as_dict(body.get("attributes"), "attributes")
    ranks: dict[str, int] = {}
    for attr in attrs_cfg:
        if attr not in raw_attrs:
            raise CreateError(f"attributes.{attr} is required")
        try:
            rank = int(raw_attrs[attr])
        except (TypeError, ValueError) as e:
            raise CreateError(f"attributes.{attr} must be an integer") from e
        if rank < 0 or rank > max_rank:
            raise CreateError(f"attributes.{attr} must be between 0 and {max_rank}")
        ranks[attr] = rank
    for extra in raw_attrs:
        if str(extra).strip().lower() not in attrs_cfg:
            raise CreateError(f"unknown attribute: {extra}")

    spent = attribute_spend(ranks, cost_for_rank)
    if spent != pool:
        raise CreateError(f"attribute spend must equal {pool} (got {spent})")

    attr_traits = expand_attribute_traits(ranks, abbreviations, pattern)
    for tid in attr_traits:
        if tid not in traits_by_id:
            raise CreateError(f"attribute trait missing from catalog: {tid}")

    # Soft slot check (per-player entitlement if synced, else catalog default)
    max_alive = get_max_alive(player_uuid, slot_limits)
    alive = count_alive(player_uuid)
    if alive >= max_alive:
        raise CreateError("no free character slot")

    merged_traits = list(dict.fromkeys([*selected_traits, *attr_traits]))

    client_request_id = body.get("client_request_id")
    if client_request_id is not None:
        client_request_id = str(client_request_id).strip() or None

    return {
        "client_request_id": client_request_id,
        "name": name,
        "age": age,
        "description": description,
        "gender": gender,
        "race_id": race_id,
        "class_id": class_id,
        "attributes": ranks,
        "traits": selected_traits,
        "attribute_traits": attr_traits,
        "all_traits": merged_traits,
        "clues": clues,
    }


def _row_to_dict(row) -> dict[str, Any]:
    payload = {}
    try:
        payload = json.loads(row["payload"] or "{}")
    except json.JSONDecodeError:
        payload = {}
    return {
        "id": row["id"],
        "player_uuid": row["player_uuid"],
        "client_request_id": row["client_request_id"],
        "status": row["status"],
        "character_id": row["character_id"],
        "error": row["error"],
        "created_at": row["created_at"],
        "applied_at": row["applied_at"],
        "payload": payload,
    }


def create_character(player_uuid: str, body: dict[str, Any]) -> dict[str, Any]:
    from src.skins.db import connect

    uuid = (player_uuid or "").strip()
    if not uuid:
        raise CreateError("player_uuid is required")
    if not isinstance(body, dict):
        raise CreateError("body must be a JSON object")

    try:
        normalized = _validate_and_normalize(uuid, body)
    except CreationCatalogError as e:
        raise CreateError(str(e)) from e

    client_request_id = normalized.get("client_request_id")
    with connect() as conn:
        if client_request_id:
            existing = conn.execute(
                """
                SELECT * FROM character_creates
                WHERE player_uuid = ? AND client_request_id = ?
                """,
                (uuid, client_request_id),
            ).fetchone()
            if existing is not None:
                return _row_to_dict(existing)

        create_id = str(uuid_lib.uuid4())
        now = _iso_now()
        payload = json.dumps(normalized, separators=(",", ":"))
        conn.execute(
            """
            INSERT INTO character_creates (
                id, player_uuid, client_request_id, payload, status,
                character_id, error, created_at, applied_at
            )
            VALUES (?, ?, ?, ?, 'pending', NULL, NULL, ?, NULL)
            """,
            (create_id, uuid, client_request_id, payload, now),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM character_creates WHERE id = ?",
            (create_id,),
        ).fetchone()
    return _row_to_dict(row)


def list_pending() -> list[dict[str, Any]]:
    from src.skins.db import connect

    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM character_creates
            WHERE status = 'pending'
            ORDER BY created_at ASC
            """
        ).fetchall()
    return [_row_to_dict(r) for r in rows]


def list_for_player(player_uuid: str) -> dict[str, Any]:
    from src.characters.creation_catalog import get_catalog
    from src.characters.roster import count_alive, get_max_alive, list_roster
    from src.skins.db import connect

    uuid = (player_uuid or "").strip()
    roster = list_roster(uuid)
    with connect() as conn:
        pending_rows = conn.execute(
            """
            SELECT * FROM character_creates
            WHERE player_uuid = ? AND status = 'pending'
            ORDER BY created_at ASC
            """,
            (uuid,),
        ).fetchall()

    characters: list[dict[str, Any]] = list(roster)
    for row in pending_rows:
        data = _row_to_dict(row)
        payload = data.get("payload") or {}
        characters.append(
            {
                "id": data["id"],
                "name": payload.get("name") or "(pending)",
                "status": "pending",
                "race": payload.get("race_id"),
                "class": payload.get("class_id"),
                "created_at": data["created_at"],
                "source": "create",
                "create_id": data["id"],
            }
        )

    catalog = get_catalog()
    raw_limits = catalog.get("slot_limits")
    slot_limits = raw_limits if isinstance(raw_limits, dict) else {}

    max_alive = get_max_alive(uuid, slot_limits)
    alive_count = count_alive(uuid)
    return {
        "characters": characters,
        "player_uuid": uuid,
        "max_alive_characters": max_alive,
        "alive_count": alive_count,
    }


def mark_applied_results(results: list) -> dict[str, Any]:
    from src.skins.db import connect

    if not isinstance(results, list):
        raise CreateError("results must be a list")

    now = _iso_now()
    applied: list[str] = []
    rejected: list[str] = []

    with connect() as conn:
        for i, raw in enumerate(results):
            if not isinstance(raw, dict):
                raise CreateError(f"results[{i}] must be an object")
            cid = str(raw.get("id") or "").strip()
            if not cid:
                continue
            ok = bool(raw.get("ok"))
            if ok:
                character_id = str(raw.get("character_id") or cid).strip()
                cur = conn.execute(
                    """
                    UPDATE character_creates
                    SET status = 'applied',
                        character_id = ?,
                        error = NULL,
                        applied_at = ?
                    WHERE id = ? AND status = 'pending'
                    """,
                    (character_id, now, cid),
                )
                if cur.rowcount:
                    applied.append(cid)
            else:
                error = str(raw.get("error") or "rejected").strip()
                cur = conn.execute(
                    """
                    UPDATE character_creates
                    SET status = 'rejected',
                        error = ?,
                        applied_at = ?
                    WHERE id = ? AND status = 'pending'
                    """,
                    (error, now, cid),
                )
                if cur.rowcount:
                    rejected.append(cid)
        conn.commit()

    return {"ok": True, "applied": applied, "rejected": rejected}
