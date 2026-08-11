"""Character lore-item customise API (kit editable parts + skin bridge)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from src.skins.submissions import (
    MAX_DISPLAY_NAME,
    SubmissionError,
    create_submission,
)
from src.skins.storage import StorageError
from src.text_validation import TextValidationError, assert_display_name, assert_prose

LORE_MAX_LINES = 6
LORE_LINE_MAX_LEN = 48

STATE_DRAFT = "draft"
STATE_PENDING_SKIN = "pending_skin"
STATE_READY = "ready"
STATE_APPLIED = "applied"

# Sentinel: omit existing_skin_id → leave skin refs unchanged.
_UNSET = object()


class LoreItemError(ValueError):
    """Business-rule failure for lore-item routes."""

    def __init__(self, message: str, *, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _require_character_id(character_id: str | None) -> str:
    cid = (character_id or "").strip()
    if not cid:
        raise LoreItemError("character_id is required", status_code=400)
    return cid


_CLAIMABLE_KIT = frozenset({"eligible", "ineligible"})


def _kit_statuses_for_character(
    player_uuid: str, character_id: str
) -> dict[str, str] | None:
    """Return kit_id → status for a roster character, or None if not on roster."""
    from src.skins.db import connect

    uuid = (player_uuid or "").strip()
    cid = (character_id or "").strip()
    if not uuid or not cid:
        return None
    with connect() as conn:
        row = conn.execute(
            """
            SELECT kit_status, kit_statuses_json
            FROM character_roster
            WHERE player_uuid = ? AND character_id = ?
            """,
            (uuid, cid),
        ).fetchone()
    if row is None:
        return None
    statuses: dict[str, str] = {}
    try:
        raw = row["kit_statuses_json"]
    except (KeyError, IndexError):
        raw = None
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                for k, v in parsed.items():
                    if k is None or v is None:
                        continue
                    kid = str(k).strip().lower()
                    if kid:
                        statuses[kid] = str(v).strip().lower()
        except (TypeError, json.JSONDecodeError):
            pass
    if not statuses:
        kit_status = row["kit_status"]
        if kit_status is not None and str(kit_status).strip():
            statuses["starter"] = str(kit_status).strip().lower()
    return statuses


def _catalog_kit(kit_id: str) -> dict[str, Any] | None:
    from src.characters.creation_catalog import get_catalog

    kit = (kit_id or "starter").strip().lower() or "starter"
    kits = get_catalog().get("kits") or []
    if not isinstance(kits, list):
        return None
    for row in kits:
        if not isinstance(row, dict):
            continue
        if str(row.get("id") or "").strip().lower() == kit:
            return row
    return None


def _is_kit_claimable(kit_def: dict[str, Any] | None, status: str | None) -> bool:
    """Customise allowed when the character can still claim that kit."""
    st = (status or "eligible").strip().lower() or "eligible"
    once = True
    if kit_def is not None:
        once = bool(kit_def.get("once_per_character", True))
    if not once:
        return True
    return st in _CLAIMABLE_KIT or st == ""


def _require_customise_allowed(
    player_uuid: str,
    character_id: str,
    kit_id: str | None = None,
) -> None:
    """Allow customise only for roster characters while that kit is claimable."""
    uuid = (player_uuid or "").strip()
    cid = (character_id or "").strip()
    kit = (kit_id or "starter").strip().lower() or "starter"
    statuses = _kit_statuses_for_character(uuid, cid)
    if statuses is None:
        raise LoreItemError(
            "Character not found on roster",
            status_code=403,
        )
    kit_def = _catalog_kit(kit)
    status = statuses.get(kit)
    if status is None and kit == "starter":
        status = statuses.get("starter")
    if not _is_kit_claimable(kit_def, status):
        raise LoreItemError(
            "Kit already claimed; customise is only before claim",
            status_code=403,
        )


def remount_character_id(
    player_uuid: str, create_id: str, character_id: str
) -> int:
    """Move lore_item_customisations from create UUID onto real character_id.

    Create-scoped rows replace any existing rows for the same kit_key on the
    real character. Returns number of rows remounted.
    """
    from src.skins.db import connect

    uuid = (player_uuid or "").strip()
    from_id = (create_id or "").strip()
    to_id = (character_id or "").strip()
    if not uuid or not from_id or not to_id or from_id == to_id:
        return 0

    remounted = 0
    now = _iso_now()
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT kit_key FROM lore_item_customisations
            WHERE player_uuid = ? AND character_id = ?
            """,
            (uuid, from_id),
        ).fetchall()
        for row in rows:
            kit_key = str(row["kit_key"] or "").strip()
            if not kit_key:
                continue
            conn.execute(
                """
                DELETE FROM lore_item_customisations
                WHERE player_uuid = ? AND character_id = ? AND kit_key = ?
                """,
                (uuid, to_id, kit_key),
            )
            cur = conn.execute(
                """
                UPDATE lore_item_customisations
                SET character_id = ?, updated_at = ?
                WHERE player_uuid = ? AND character_id = ? AND kit_key = ?
                """,
                (to_id, now, uuid, from_id, kit_key),
            )
            remounted += int(cur.rowcount or 0)
        conn.commit()
    return remounted


def claim_status(
    player_uuid: str,
    character_id: str,
    kit_id: str | None = None,
) -> dict[str, Any]:
    """Plugin helper: whether claim should wait on pending_skin / has ready rows.

    When ``kit_id`` is set, only customisations whose ``kit_key`` belongs to that
    kit (from catalog ``editable_kit`` / ``kits``) are considered. Fallback when
    kits payload is missing: for ``starter`` (default), any row for the character.
    """
    from src.skins.db import connect

    uuid = (player_uuid or "").strip()
    cid = (character_id or "").strip()
    kit = (kit_id or "starter").strip().lower() or "starter"
    pending_skin = False
    ready = False
    if not uuid or not cid:
        return {"pending_skin": False, "ready": False, "kit_id": kit}

    allowed_keys = _kit_editable_keys(kit)
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT LOWER(COALESCE(state, '')) AS state,
                   LOWER(COALESCE(kit_key, '')) AS kit_key
            FROM lore_item_customisations
            WHERE player_uuid = ? AND character_id = ?
            """,
            (uuid, cid),
        ).fetchall()
    for row in rows:
        key = str(row["kit_key"] or "").strip().lower()
        if allowed_keys is not None and key not in allowed_keys:
            continue
        state = str(row["state"] or "").strip().lower()
        if state == STATE_PENDING_SKIN:
            pending_skin = True
        elif state == STATE_READY:
            ready = True
    return {"pending_skin": pending_skin, "ready": ready, "kit_id": kit}


def _kit_editable_keys(kit_id: str) -> set[str] | None:
    """Return kit_key set for ``kit_id``, or None to mean 'any key' (fallback)."""
    from src.characters.creation_catalog import get_catalog

    kit = (kit_id or "starter").strip().lower() or "starter"
    catalog = get_catalog()
    keys: set[str] = set()

    kits = catalog.get("kits")
    if isinstance(kits, list) and kits:
        for row in kits:
            if not isinstance(row, dict):
                continue
            if str(row.get("id") or "").strip().lower() != kit:
                continue
            items = row.get("items")
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict):
                    continue
                if not item.get("editable"):
                    continue
                path = str(item.get("path") or "").strip()
                if not path:
                    continue
                keys.add(_kit_key_from_path(path))
            return keys

    editable = catalog.get("editable_kit") or []
    if isinstance(editable, list) and editable:
        tagged = False
        for row in editable:
            if not isinstance(row, dict):
                continue
            row_kit = str(row.get("kit_id") or "").strip().lower()
            if row_kit:
                tagged = True
            if row_kit == kit:
                key = str(row.get("kit_key") or "").strip().lower()
                if key:
                    keys.add(key)
        if tagged:
            return keys
        # Untagged flat editable_kit: only filter for starter (character-wide).
        if kit == "starter":
            return None
        return set()

    # No kits / editable payload yet.
    if kit == "starter":
        return None
    return set()


def _kit_key_from_path(path: str) -> str:
    segment = path.rsplit(".", 1)[-1] if path else ""
    return segment.strip().lower()


def _editable_rows() -> list[dict[str, Any]]:
    from src.characters.creation_catalog import get_catalog

    catalog = get_catalog()
    raw = catalog.get("editable_kit") or []
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for row in raw:
        if isinstance(row, dict) and str(row.get("kit_key") or "").strip():
            out.append(row)
    return out


def _editable_by_key(kit_key: str) -> dict[str, Any]:
    key = (kit_key or "").strip().lower()
    for row in _editable_rows():
        if str(row.get("kit_key") or "").strip().lower() == key:
            return row
    raise LoreItemError(f"Unknown editable kit key '{kit_key}'", status_code=404)


def _path_for_kit_key(kit_key: str) -> str:
    try:
        return str(_editable_by_key(kit_key).get("path") or "").strip()
    except LoreItemError:
        return ""


def _parse_lore_json(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return [str(line) for line in data if line is not None]


def _validate_lore(lore: list[str] | None) -> list[str]:
    if lore is None:
        return []
    if not isinstance(lore, list):
        raise LoreItemError("lore must be a list")
    if len(lore) > LORE_MAX_LINES:
        raise LoreItemError(f"lore must have at most {LORE_MAX_LINES} lines")
    out: list[str] = []
    for i, line in enumerate(lore):
        try:
            out.append(
                assert_prose(
                    line,
                    min_len=1,
                    max_len=LORE_LINE_MAX_LEN,
                    field=f"lore[{i}]",
                )
            )
        except TextValidationError as e:
            raise LoreItemError(str(e)) from e
    return out


def _validate_display_name(raw: str | None) -> str:
    try:
        return assert_display_name(
            raw,
            min_len=1,
            max_len=MAX_DISPLAY_NAME,
            field="display name",
        )
    except TextValidationError as e:
        raise LoreItemError(str(e)) from e


def _base_preview(editable: dict[str, Any]) -> dict[str, Any]:
    preview = editable.get("preview")
    if not isinstance(preview, dict):
        return {
            "display_name": "",
            "lore": [],
            "material": "",
        }
    lore_raw = preview.get("lore")
    lore = (
        [str(line) for line in lore_raw if line is not None]
        if isinstance(lore_raw, list)
        else []
    )
    out: dict[str, Any] = {
        "display_name": str(preview.get("display_name") or ""),
        "lore": lore,
        "material": str(preview.get("material") or ""),
    }
    cmd = preview.get("custom_model_data")
    if cmd is not None:
        try:
            out["custom_model_data"] = int(cmd)
        except (TypeError, ValueError):
            pass
    return out


def _merge_preview(
    base: dict[str, Any],
    draft_name: str,
    draft_lore: list[str],
) -> dict[str, Any]:
    name = draft_name.strip() if draft_name and draft_name.strip() else base.get(
        "display_name", ""
    )
    base_lore = list(base.get("lore") or [])
    merged_lore = base_lore + list(draft_lore or [])
    out: dict[str, Any] = {
        "display_name": name,
        "lore": merged_lore,
        "material": base.get("material") or "",
    }
    if "custom_model_data" in base:
        out["custom_model_data"] = base["custom_model_data"]
    return out


def _row_keys(row: Any) -> set[str]:
    try:
        return set(row.keys())
    except Exception:
        return set()


def _load_row(
    player_uuid: str, character_id: str, kit_key: str
) -> dict[str, Any] | None:
    from src.skins.db import connect

    with connect() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM lore_item_customisations
            WHERE player_uuid = ? AND character_id = ? AND kit_key = ?
            """,
            (player_uuid, character_id, kit_key),
        ).fetchone()
    if row is None:
        return None
    keys = _row_keys(row)
    submission_id = row["submission_id"]
    submission_status = None
    if submission_id:
        with connect() as conn:
            sub = conn.execute(
                "SELECT status FROM submissions WHERE id = ?",
                (submission_id,),
            ).fetchone()
        if sub is not None:
            submission_status = str(sub["status"] or "")
    return {
        "display_name": str(row["display_name"] or ""),
        "lore": _parse_lore_json(row["lore_json"]),
        "existing_skin_id": row["existing_skin_id"],
        "submission_id": submission_id,
        "submission_status": submission_status,
        "state": str(row["state"] if "state" in keys else STATE_DRAFT) or STATE_DRAFT,
        "skin_slug": row["skin_slug"] if "skin_slug" in keys else None,
        "ready_at": row["ready_at"] if "ready_at" in keys else None,
        "applied_at": row["applied_at"] if "applied_at" in keys else None,
    }


def _load_draft(
    player_uuid: str, character_id: str, kit_key: str
) -> dict[str, Any]:
    row = _load_row(player_uuid, character_id, kit_key)
    if row is None:
        return {
            "display_name": "",
            "lore": [],
            "existing_skin_id": None,
            "submission_id": None,
            "submission_status": None,
            "state": STATE_DRAFT,
            "skin_slug": None,
            "ready_at": None,
            "applied_at": None,
        }
    return row


def _list_pickable_skins(base_set: str) -> list[dict[str, Any]]:
    from src.skins.db import connect

    base = (base_set or "").strip().lower()
    if not base:
        return []
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT id, display_name, kind
            FROM submissions
            WHERE LOWER(COALESCE(base_set, '')) = ?
              AND LOWER(status) = 'applied'
            ORDER BY display_name COLLATE NOCASE ASC, id ASC
            """,
            (base,),
        ).fetchall()
    return [
        {
            "id": row["id"],
            "display_name": row["display_name"],
            "kind": row["kind"],
        }
        for row in rows
    ]


def _validate_existing_skin(skin_id: str, base_set: str) -> str:
    from src.skins.db import connect

    sid = (skin_id or "").strip()
    if not sid:
        raise LoreItemError("existing_skin_id is required when provided")
    base = (base_set or "").strip().lower()
    with connect() as conn:
        row = conn.execute(
            """
            SELECT id, base_set, status
            FROM submissions
            WHERE id = ?
            """,
            (sid,),
        ).fetchone()
    if row is None:
        raise LoreItemError("existing_skin_id not found", status_code=400)
    if str(row["status"] or "").strip().lower() != "applied":
        raise LoreItemError(
            "existing_skin_id must be an applied skin",
            status_code=400,
        )
    row_base = str(row["base_set"] or "").strip().lower()
    if row_base != base:
        raise LoreItemError(
            f"existing_skin_id base_set must be '{base}'",
            status_code=400,
        )
    return sid


def _ia_path(skin_slug: str | None) -> str | None:
    slug = (skin_slug or "").strip()
    if not slug:
        return None
    return f"ia.tfmc_submissions:{slug}"


def _build_item(
    player_uuid: str,
    character_id: str,
    editable: dict[str, Any],
) -> dict[str, Any]:
    kit_key = str(editable.get("kit_key") or "").strip()
    base_set = str(editable.get("base_set") or "").strip()
    base_preview = _base_preview(editable)
    draft = _load_draft(player_uuid, character_id, kit_key)
    preview = _merge_preview(
        base_preview, draft["display_name"], draft["lore"]
    )
    return {
        "kit_key": kit_key,
        "path": str(editable.get("path") or ""),
        "skin_png": str(editable.get("skin_png") or ""),
        "base_set": base_set,
        "eligible": True,
        "base_preview": base_preview,
        "preview": preview,
        "draft": draft,
        "state": draft.get("state") or STATE_DRAFT,
        "skin_slug": draft.get("skin_slug"),
        "pickable_skins": _list_pickable_skins(base_set),
    }


def list_lore_items(
    player_uuid: str,
    character_id: str | None,
    kit_id: str | None = None,
) -> dict[str, Any]:
    """List editable kit parts + drafts for a claimable kit on a roster character."""
    uuid = (player_uuid or "").strip()
    if not uuid:
        raise LoreItemError("player_uuid is required", status_code=401)
    cid = _require_character_id(character_id)
    kit = (kit_id or "starter").strip().lower() or "starter"
    _require_customise_allowed(uuid, cid, kit)
    allowed = _kit_editable_keys(kit)
    items: list[dict[str, Any]] = []
    for editable in _editable_rows():
        row_kit = str(editable.get("kit_id") or "").strip().lower()
        key = str(editable.get("kit_key") or "").strip().lower()
        if row_kit and row_kit != kit:
            continue
        if allowed is not None:
            if key not in allowed:
                continue
        elif kit != "starter":
            continue
        item = _build_item(uuid, cid, editable)
        item["kit_id"] = row_kit or kit
        items.append(item)
    return {"character_id": cid, "kit_id": kit, "items": items}


def list_character_kits(player_uuid: str, character_id: str | None) -> dict[str, Any]:
    """Full kits list for a roster character (all items + claimability)."""
    from src.characters.creation_catalog import get_catalog
    from src.characters.roster import get_player_meta

    uuid = (player_uuid or "").strip()
    if not uuid:
        raise LoreItemError("player_uuid is required", status_code=401)
    cid = _require_character_id(character_id)
    statuses = _kit_statuses_for_character(uuid, cid)
    if statuses is None:
        raise LoreItemError(
            "Character not found on roster",
            status_code=403,
        )
    catalog = get_catalog()
    kits_raw = catalog.get("kits") or []
    if not isinstance(kits_raw, list):
        kits_raw = []
    editable_by_key: dict[str, dict[str, Any]] = {}
    for row in _editable_rows():
        key = str(row.get("kit_key") or "").strip().lower()
        if key:
            editable_by_key[key] = row
    meta = get_player_meta(uuid)
    cooldowns = (
        meta.get("kit_cooldowns")
        if isinstance(meta.get("kit_cooldowns"), dict)
        else {}
    )

    out_kits: list[dict[str, Any]] = []
    for kit_row in kits_raw:
        if not isinstance(kit_row, dict):
            continue
        kid = str(kit_row.get("id") or "").strip().lower()
        if not kid:
            continue
        status = statuses.get(kid) or "eligible"
        claimable = _is_kit_claimable(kit_row, status)
        cd_raw = cooldowns.get(kid) if isinstance(cooldowns, dict) else None
        cooldown = None
        if isinstance(cd_raw, dict):
            try:
                cooldown = {
                    "seconds_remaining": max(
                        0, int(cd_raw.get("seconds_remaining") or 0)
                    ),
                    "hours": max(
                        0,
                        int(
                            cd_raw.get("hours")
                            or kit_row.get("cooldown_hours")
                            or 0
                        ),
                    ),
                }
            except (TypeError, ValueError):
                cooldown = None
        elif kid == "starter":
            try:
                secs = int(meta.get("kit_cooldown_seconds_remaining") or 0)
                hours = meta.get("kit_cooldown_hours")
                if hours is None:
                    hours = kit_row.get("cooldown_hours") or 0
                cooldown = {
                    "seconds_remaining": max(0, secs),
                    "hours": max(0, int(hours or 0)),
                }
            except (TypeError, ValueError):
                cooldown = None

        items_out: list[dict[str, Any]] = []
        items_raw = (
            kit_row.get("items") if isinstance(kit_row.get("items"), list) else []
        )
        for item in items_raw:
            if not isinstance(item, dict):
                continue
            path = str(item.get("path") or "").strip()
            if not path:
                continue
            try:
                amount = max(1, int(item.get("amount", 1)))
            except (TypeError, ValueError):
                amount = 1
            editable = bool(item.get("editable"))
            entry: dict[str, Any] = {
                "path": path,
                "amount": amount,
                "editable": editable,
            }
            if editable:
                kit_key = _kit_key_from_path(path)
                entry["kit_key"] = kit_key
                ed = editable_by_key.get(kit_key)
                if ed:
                    if ed.get("preview"):
                        entry["preview"] = _base_preview(ed)
                    entry["skin_png"] = str(ed.get("skin_png") or "")
                    entry["base_set"] = str(ed.get("base_set") or "")
                entry["customise"] = _load_draft(uuid, cid, kit_key)
            items_out.append(entry)

        out_kits.append(
            {
                "id": kid,
                "display_name": str(kit_row.get("display_name") or kid),
                "cooldown_hours": int(kit_row.get("cooldown_hours") or 0),
                "once_per_character": bool(
                    kit_row.get("once_per_character", True)
                ),
                "status": status,
                "claimable": claimable,
                "cooldown": cooldown,
                "items": items_out,
            }
        )

    return {"character_id": cid, "kits": out_kits}


def customise_lore_item(
    session_row: dict,
    character_id: str | None,
    kit_key: str,
    *,
    display_name: str | None,
    lore: list[str] | None,
    existing_skin_id: Any = _UNSET,
    texture_bytes: bytes | None = None,
    kit_id: str | None = None,
) -> dict[str, Any]:
    """Validate and store customise draft; optionally bridge a new skin upload."""
    from src.skins.db import connect

    player_uuid = str(session_row.get("player_uuid") or "").strip()
    if not player_uuid:
        raise LoreItemError("Invalid session", status_code=401)
    cid = _require_character_id(character_id)
    kit = (kit_id or "starter").strip().lower() or "starter"
    _require_customise_allowed(player_uuid, cid, kit)

    key = (kit_key or "").strip()
    if not key:
        raise LoreItemError("kit_key is required", status_code=400)
    editable = _editable_by_key(key)
    row_kit = str(editable.get("kit_id") or "").strip().lower()
    if row_kit and row_kit != kit:
        raise LoreItemError(
            f"kit_key '{key}' does not belong to kit '{kit}'",
            status_code=400,
        )
    allowed = _kit_editable_keys(kit)
    kit_key_norm = str(editable.get("kit_key") or "").strip()
    if allowed is not None and kit_key_norm.lower() not in allowed:
        raise LoreItemError(
            f"kit_key '{key}' does not belong to kit '{kit}'",
            status_code=400,
        )
    base_set = str(editable.get("base_set") or "").strip()

    if texture_bytes is not None and existing_skin_id is not _UNSET and existing_skin_id:
        raise LoreItemError(
            "Provide either texture upload or existing_skin_id, not both"
        )

    name = _validate_display_name(display_name)
    lore_lines = _validate_lore(lore)

    prev = _load_draft(player_uuid, cid, kit_key_norm)
    next_existing = prev.get("existing_skin_id")
    next_submission = prev.get("submission_id")
    next_slug = prev.get("skin_slug")
    next_state = prev.get("state") or STATE_DRAFT
    next_ready_at = prev.get("ready_at")
    next_applied_at = prev.get("applied_at")
    now = _iso_now()

    if texture_bytes is not None:
        if not texture_bytes:
            raise LoreItemError("texture file is empty")
        try:
            created = create_submission(
                session_row,
                kind="handheld",
                display_name=name,
                files_bytes={"texture": texture_bytes},
                base_set=base_set or None,
                add_name=True,
            )
        except (SubmissionError, StorageError) as e:
            raise LoreItemError(str(e)) from e
        next_submission = created.get("id")
        next_existing = None
        next_slug = None
        next_state = STATE_PENDING_SKIN
        next_ready_at = None
    elif existing_skin_id is not _UNSET and existing_skin_id is not None:
        sid = str(existing_skin_id).strip()
        if sid:
            next_existing = _validate_existing_skin(sid, base_set)
            next_submission = None
            next_slug = next_existing
            next_state = STATE_READY
            next_ready_at = now
    else:
        if next_submission and (prev.get("state") or "") == STATE_PENDING_SKIN:
            next_state = STATE_PENDING_SKIN
            next_ready_at = prev.get("ready_at")
        else:
            next_state = STATE_READY
            next_ready_at = now

    lore_json = json.dumps(lore_lines, separators=(",", ":"))
    with connect() as conn:
        cols = {
            r["name"]
            for r in conn.execute(
                "PRAGMA table_info(lore_item_customisations)"
            ).fetchall()
        }
        if "kit_id" in cols:
            conn.execute(
                """
                INSERT INTO lore_item_customisations (
                    player_uuid, character_id, kit_key,
                    display_name, lore_json,
                    existing_skin_id, submission_id,
                    state, skin_slug, ready_at, applied_at, kit_id, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(player_uuid, character_id, kit_key) DO UPDATE SET
                    display_name = excluded.display_name,
                    lore_json = excluded.lore_json,
                    existing_skin_id = excluded.existing_skin_id,
                    submission_id = excluded.submission_id,
                    state = excluded.state,
                    skin_slug = excluded.skin_slug,
                    ready_at = excluded.ready_at,
                    applied_at = excluded.applied_at,
                    kit_id = excluded.kit_id,
                    updated_at = excluded.updated_at
                """,
                (
                    player_uuid,
                    cid,
                    kit_key_norm,
                    name,
                    lore_json,
                    next_existing,
                    next_submission,
                    next_state,
                    next_slug,
                    next_ready_at,
                    next_applied_at,
                    kit,
                    now,
                ),
            )
        else:
            conn.execute(
                """
                INSERT INTO lore_item_customisations (
                    player_uuid, character_id, kit_key,
                    display_name, lore_json,
                    existing_skin_id, submission_id,
                    state, skin_slug, ready_at, applied_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(player_uuid, character_id, kit_key) DO UPDATE SET
                    display_name = excluded.display_name,
                    lore_json = excluded.lore_json,
                    existing_skin_id = excluded.existing_skin_id,
                    submission_id = excluded.submission_id,
                    state = excluded.state,
                    skin_slug = excluded.skin_slug,
                    ready_at = excluded.ready_at,
                    applied_at = excluded.applied_at,
                    updated_at = excluded.updated_at
                """,
                (
                    player_uuid,
                    cid,
                    kit_key_norm,
                    name,
                    lore_json,
                    next_existing,
                    next_submission,
                    next_state,
                    next_slug,
                    next_ready_at,
                    next_applied_at,
                    now,
                ),
            )
        conn.commit()

    item = _build_item(player_uuid, cid, editable)
    item["kit_id"] = kit
    return {"ok": True, **item}



def promote_ready_for_submissions(submission_ids: list[str]) -> int:
    """When skins reach applied, promote matching pending_skin customise rows."""
    from src.skins.db import connect

    ids = [str(s).strip() for s in submission_ids if str(s or "").strip()]
    if not ids:
        return 0
    now = _iso_now()
    promoted = 0
    with connect() as conn:
        for sid in ids:
            cur = conn.execute(
                """
                UPDATE lore_item_customisations
                SET skin_slug = ?,
                    state = CASE
                        WHEN LOWER(COALESCE(state, '')) = 'applied' THEN 'applied'
                        ELSE ?
                    END,
                    ready_at = COALESCE(ready_at, ?),
                    updated_at = ?
                WHERE submission_id = ?
                """,
                (sid, STATE_READY, now, now, sid),
            )
            promoted += int(cur.rowcount or 0)
        conn.commit()
    return promoted


def clear_pending_submission(submission_id: str) -> int:
    """On deny: drop pending submission link; keep last applied snapshot fields."""
    from src.skins.db import connect

    sid = (submission_id or "").strip()
    if not sid:
        return 0
    now = _iso_now()
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT player_uuid, character_id, kit_key, applied_at, skin_slug
            FROM lore_item_customisations
            WHERE submission_id = ?
            """,
            (sid,),
        ).fetchall()
        cleared = 0
        for row in rows:
            if row["applied_at"]:
                next_state = STATE_APPLIED
            elif row["skin_slug"]:
                next_state = STATE_READY
            else:
                next_state = STATE_DRAFT
            conn.execute(
                """
                UPDATE lore_item_customisations
                SET submission_id = NULL,
                    state = ?,
                    updated_at = ?
                WHERE player_uuid = ? AND character_id = ? AND kit_key = ?
                """,
                (
                    next_state,
                    now,
                    row["player_uuid"],
                    row["character_id"],
                    row["kit_key"],
                ),
            )
            cleared += 1
        conn.commit()
    return cleared


def list_pending_for_plugin() -> list[dict[str, Any]]:
    """Rows with state=ready for RPCharacters pull."""
    from src.skins.db import connect

    with connect() as conn:
        rows = conn.execute(
            """
            SELECT player_uuid, character_id, kit_key, display_name, lore_json,
                   skin_slug, ready_at, updated_at
            FROM lore_item_customisations
            WHERE LOWER(COALESCE(state, '')) = ?
            ORDER BY ready_at ASC, updated_at ASC
            """,
            (STATE_READY,),
        ).fetchall()
    out: list[dict[str, Any]] = []
    for row in rows:
        kit_key = str(row["kit_key"] or "").strip()
        slug = row["skin_slug"]
        out.append(
            {
                "player_uuid": row["player_uuid"],
                "character_id": row["character_id"],
                "kit_key": kit_key,
                "path": _path_for_kit_key(kit_key),
                "display_name": str(row["display_name"] or ""),
                "lore": _parse_lore_json(row["lore_json"]),
                "skin_slug": slug,
                "ia_path": _ia_path(slug),
                "ready_at": row["ready_at"],
                "updated_at": row["updated_at"],
            }
        )
    return out


def mark_lore_items_applied(results: list) -> dict[str, Any]:
    """Ack plugin apply results → state=applied."""
    from src.skins.db import connect

    if not isinstance(results, list):
        raise LoreItemError("results must be a list")
    now = _iso_now()
    ok_n = 0
    fail_n = 0
    with connect() as conn:
        for i, raw in enumerate(results):
            if not isinstance(raw, dict):
                raise LoreItemError(f"results[{i}] must be an object")
            cid = str(raw.get("character_id") or "").strip()
            kit_key = str(raw.get("kit_key") or "").strip()
            player_uuid = str(raw.get("player_uuid") or "").strip()
            ok = bool(raw.get("ok"))
            if not cid or not kit_key:
                raise LoreItemError(
                    f"results[{i}] requires character_id and kit_key"
                )
            if not ok:
                fail_n += 1
                continue
            if player_uuid:
                cur = conn.execute(
                    """
                    UPDATE lore_item_customisations
                    SET state = ?, applied_at = ?, updated_at = ?
                    WHERE player_uuid = ?
                      AND character_id = ?
                      AND kit_key = ?
                      AND LOWER(COALESCE(state, '')) = ?
                    """,
                    (
                        STATE_APPLIED,
                        now,
                        now,
                        player_uuid,
                        cid,
                        kit_key,
                        STATE_READY,
                    ),
                )
            else:
                cur = conn.execute(
                    """
                    UPDATE lore_item_customisations
                    SET state = ?, applied_at = ?, updated_at = ?
                    WHERE character_id = ?
                      AND kit_key = ?
                      AND LOWER(COALESCE(state, '')) = ?
                    """,
                    (STATE_APPLIED, now, now, cid, kit_key, STATE_READY),
                )
            if cur.rowcount:
                ok_n += 1
            else:
                fail_n += 1
        conn.commit()
    return {"ok": True, "applied": ok_n, "failed": fail_n}
