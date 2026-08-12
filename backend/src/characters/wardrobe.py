"""Character skin wardrobe CRUD (player skins per slot)."""

from __future__ import annotations

import io
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image

from src.characters.wardrobe_sign import sign_wardrobe_skin
from src.characters.roster import get_wardrobe_skin_slots
from src.skins.db import DATA_DIR, WARDROBE_DIR, connect
from src.skins.storage import StorageError, validate_png
from src.text_validation import TextValidationError, assert_optional_display_name

SLOTS = ("base", "extra_1", "extra_2", "masked")
SWAPPABLE_SLOTS = frozenset({"base", "extra_1", "extra_2"})
WARDROBE_PNG_SIZE = (64, 64)
DEFAULT_SLOT_NAMES = {
    "base": "Base",
    "extra_1": "Skin 2",
    "extra_2": "Skin 3",
    "masked": "Masked",
}
DISPLAY_NAME_MAX = 24


class WardrobeError(ValueError):
    """Business-rule failure for wardrobe routes."""

    def __init__(self, message: str, *, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def swappable_slot_count(player_uuid: str) -> int:
    """Number of swappable skins (base + extras). From roster meta perk."""
    return get_wardrobe_skin_slots(player_uuid)


def _slot_unlocked(slot: str, swappable: int) -> bool:
    if slot == "base" or slot == "masked":
        return True
    if slot == "extra_1":
        return swappable >= 2
    if slot == "extra_2":
        return swappable >= 3
    return False


def _normalize_slot(slot: str | None) -> str:
    s = (slot or "").strip().lower()
    if s not in SLOTS:
        raise WardrobeError(
            f"Invalid slot (expected one of: {', '.join(SLOTS)})",
            status_code=400,
        )
    return s


def _require_character_id(character_id: str | None) -> str:
    cid = (character_id or "").strip()
    if not cid:
        raise WardrobeError("character_id is required", status_code=400)
    return cid


def _require_owned_character(player_uuid: str, character_id: str) -> dict[str, Any]:
    uuid = (player_uuid or "").strip()
    cid = _require_character_id(character_id)
    if not uuid:
        raise WardrobeError("player_uuid is required", status_code=400)
    with connect() as conn:
        row = conn.execute(
            """
            SELECT player_uuid, character_id, wardrobe_active_slot
            FROM character_roster
            WHERE player_uuid = ? AND character_id = ?
            """,
            (uuid, cid),
        ).fetchone()
    if row is None:
        raise WardrobeError("Character not found on roster", status_code=403)
    return dict(row)


def detect_skin_model(png_bytes: bytes) -> str:
    """Return classic or slim from a 64x64 skin PNG (arm column alpha heuristic)."""
    try:
        img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    except Exception as e:
        raise WardrobeError(f"Invalid PNG: {e}", status_code=400) from e
    if img.size != WARDROBE_PNG_SIZE:
        raise WardrobeError(
            f"PNG must be 64x64, got {img.size[0]}x{img.size[1]}",
            status_code=400,
        )
    # Right arm outer column on classic occupies x=54–55; slim leaves it empty.
    # Sample (54, 20) on the right-arm region of the base layer.
    alpha = img.getpixel((54, 20))[3]
    return "slim" if alpha == 0 else "classic"


def _png_abspath(relpath: str | None) -> Path | None:
    if not relpath:
        return None
    path = DATA_DIR / relpath
    try:
        path.resolve().relative_to(WARDROBE_DIR.resolve())
    except ValueError:
        return None
    return path if path.is_file() else None


def _slot_relpath(player_uuid: str, character_id: str, slot: str) -> str:
    return f"wardrobe/{player_uuid}/{character_id}/{slot}.png"


def _write_png(player_uuid: str, character_id: str, slot: str, data: bytes) -> str:
    rel = _slot_relpath(player_uuid, character_id, slot)
    out = DATA_DIR / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    return rel


def _delete_png(relpath: str | None) -> None:
    path = _png_abspath(relpath)
    if path is not None and path.is_file():
        path.unlink(missing_ok=True)


def _normalize_display_name(raw: str | None) -> str | None:
    try:
        return assert_optional_display_name(
            raw, max_len=DISPLAY_NAME_MAX, field="display_name"
        )
    except TextValidationError as e:
        raise WardrobeError(str(e), status_code=400) from e


def default_slot_label(slot: str) -> str:
    return DEFAULT_SLOT_NAMES.get(slot, slot)


def _effective_display_name(slot: str, row: dict[str, Any] | None) -> str:
    if row:
        custom = str(row.get("display_name") or "").strip()
        if custom:
            return custom
    return default_slot_label(slot)


def _load_slots(
    player_uuid: str, character_id: str
) -> dict[str, dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT slot, png_relpath, texture_value, texture_signature,
                   model, display_name, apply_pending, updated_at
            FROM character_wardrobe_slots
            WHERE player_uuid = ? AND character_id = ?
            """,
            (player_uuid, character_id),
        ).fetchall()
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        out[str(row["slot"])] = dict(row)
    return out


def _set_active(
    player_uuid: str, character_id: str, active: str | None
) -> None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE character_roster
            SET wardrobe_active_slot = ?
            WHERE player_uuid = ? AND character_id = ?
            """,
            (active, player_uuid, character_id),
        )
        conn.commit()


def _normalize_active(
    player_uuid: str,
    character_id: str,
    active: str | None,
    slots: dict[str, dict[str, Any]],
    swappable: int,
) -> str | None:
    """Ensure active points at an unlocked filled swappable slot, else fix."""
    if active:
        active = active.strip().lower()
    if active in SWAPPABLE_SLOTS and _slot_unlocked(active, swappable):
        row = slots.get(active)
        if row and row.get("png_relpath"):
            return active
    base = slots.get("base")
    if base and base.get("png_relpath") and _slot_unlocked("base", swappable):
        if active != "base":
            _set_active(player_uuid, character_id, "base")
        return "base"
    if active is not None:
        _set_active(player_uuid, character_id, None)
    return None


def enforce_wardrobe_slot_limits(player_uuid: str, character_id: str) -> int:
    """Delete locked extra slots (and PNGs); fix active. Returns swappable count."""
    uuid = (player_uuid or "").strip()
    cid = (character_id or "").strip()
    swappable = swappable_slot_count(uuid)
    slots = _load_slots(uuid, cid)
    wiped = False
    for slot in ("extra_1", "extra_2"):
        if _slot_unlocked(slot, swappable):
            continue
        row = slots.get(slot)
        if not row:
            continue
        _delete_png(row.get("png_relpath"))
        with connect() as conn:
            conn.execute(
                """
                DELETE FROM character_wardrobe_slots
                WHERE player_uuid = ? AND character_id = ? AND slot = ?
                """,
                (uuid, cid, slot),
            )
            conn.commit()
        wiped = True
    if wiped:
        slots = _load_slots(uuid, cid)
    with connect() as conn:
        row = conn.execute(
            """
            SELECT wardrobe_active_slot
            FROM character_roster
            WHERE player_uuid = ? AND character_id = ?
            """,
            (uuid, cid),
        ).fetchone()
    active = row["wardrobe_active_slot"] if row else None
    _normalize_active(uuid, cid, active, slots, swappable)
    return swappable


def _build_wardrobe_payload(
    player_uuid: str, character_id: str, *, include_textures: bool
) -> dict[str, Any]:
    roster = _require_owned_character(player_uuid, character_id)
    uuid = str(roster["player_uuid"])
    cid = str(roster["character_id"])
    swappable = enforce_wardrobe_slot_limits(uuid, cid)
    slots_db = _load_slots(uuid, cid)
    # Re-read active after enforce may have rewritten it
    roster = _require_owned_character(uuid, cid)
    active = _normalize_active(
        uuid,
        cid,
        roster.get("wardrobe_active_slot"),
        slots_db,
        swappable,
    )
    slot_list: list[dict[str, Any]] = []
    for slot in SLOTS:
        unlocked = _slot_unlocked(slot, swappable)
        row = slots_db.get(slot)
        filled = bool(row and row.get("png_relpath"))
        value = (row.get("texture_value") if row else None) or None
        signature = (row.get("texture_signature") if row else None) or None
        has_sig = bool(value and signature)
        entry: dict[str, Any] = {
            "slot": slot,
            "unlocked": unlocked,
            "filled": filled,
            "model": (row.get("model") if row else None),
            "display_name": _effective_display_name(slot, row),
            "custom_name": bool(
                row and str(row.get("display_name") or "").strip()
            ),
            "apply_pending": bool(row and int(row.get("apply_pending") or 0)),
            "has_signature": has_sig,
            "signed": has_sig,
            "texture_url": (
                f"/characters/{cid}/wardrobe/{slot}/texture" if filled else None
            ),
        }
        if include_textures:
            entry["texture_value"] = value if has_sig else None
            entry["texture_signature"] = signature if has_sig else None
        slot_list.append(entry)
    return {
        "character_id": cid,
        "player_uuid": uuid,
        "active_slot": active,
        "swappable_slots": swappable,
        "slots": slot_list,
    }


def get_wardrobe(player_uuid: str, character_id: str) -> dict[str, Any]:
    """Session-safe wardrobe list (no Mojang texture value/signature)."""
    return _build_wardrobe_payload(
        player_uuid, character_id, include_textures=False
    )


def get_wardrobe_for_plugin(
    player_uuid: str, character_id: str
) -> dict[str, Any]:
    """Plugin wardrobe list including signed texture value/signature."""
    return _build_wardrobe_payload(
        player_uuid, character_id, include_textures=True
    )


def upload_slot(
    player_uuid: str,
    character_id: str,
    slot: str,
    png_bytes: bytes,
    *,
    display_name: str | None = None,
) -> dict[str, Any]:
    roster = _require_owned_character(player_uuid, character_id)
    uuid = str(roster["player_uuid"])
    cid = str(roster["character_id"])
    slot_key = _normalize_slot(slot)
    swappable = enforce_wardrobe_slot_limits(uuid, cid)
    if not _slot_unlocked(slot_key, swappable):
        raise WardrobeError(
            "Slot locked for your rank",
            status_code=403,
        )
    try:
        validate_png(png_bytes, WARDROBE_PNG_SIZE)
    except StorageError as e:
        raise WardrobeError(str(e), status_code=400) from e
    model = detect_skin_model(png_bytes)

    # Sign before mutating disk/DB so failed MineSkin leaves the prior slot intact.
    texture_value, texture_signature = sign_wardrobe_skin(png_bytes, model)

    name = _normalize_display_name(display_name)
    existing = _load_slots(uuid, cid).get(slot_key)
    keep_name = (
        name
        if display_name is not None
        else (
            str(existing.get("display_name") or "").strip() or None
            if existing
            else None
        )
    )
    if existing:
        _delete_png(existing.get("png_relpath"))

    rel = _write_png(uuid, cid, slot_key, png_bytes)
    now = _iso_now()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO character_wardrobe_slots (
                player_uuid, character_id, slot, png_relpath,
                texture_value, texture_signature, model,
                display_name, apply_pending, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            ON CONFLICT(player_uuid, character_id, slot) DO UPDATE SET
                png_relpath = excluded.png_relpath,
                texture_value = excluded.texture_value,
                texture_signature = excluded.texture_signature,
                model = excluded.model,
                display_name = excluded.display_name,
                apply_pending = 1,
                updated_at = excluded.updated_at
            """,
            (
                uuid,
                cid,
                slot_key,
                rel,
                texture_value,
                texture_signature,
                model,
                keep_name,
                now,
            ),
        )
        conn.commit()

    # Auto-equip base on first fill if nothing active
    if slot_key in SWAPPABLE_SLOTS:
        current = roster.get("wardrobe_active_slot")
        slots_after = _load_slots(uuid, cid)
        normalized = _normalize_active(
            uuid, cid, current, slots_after, swappable
        )
        if normalized is None and slot_key == "base":
            _set_active(uuid, cid, "base")

    wardrobe = get_wardrobe(uuid, cid)
    wardrobe["uploaded_slot"] = slot_key
    wardrobe["signed"] = True
    return wardrobe


def set_slot_display_name(
    player_uuid: str,
    character_id: str,
    slot: str,
    display_name: str | None,
) -> dict[str, Any]:
    """Rename a filled slot. Does not re-sign or set apply_pending."""
    roster = _require_owned_character(player_uuid, character_id)
    uuid = str(roster["player_uuid"])
    cid = str(roster["character_id"])
    slot_key = _normalize_slot(slot)
    swappable = enforce_wardrobe_slot_limits(uuid, cid)
    if not _slot_unlocked(slot_key, swappable):
        raise WardrobeError(
            "Slot locked for your rank",
            status_code=403,
        )
    slots = _load_slots(uuid, cid)
    row = slots.get(slot_key)
    if not row or not row.get("png_relpath"):
        raise WardrobeError("Wardrobe slot is empty", status_code=404)
    name = _normalize_display_name(display_name)
    with connect() as conn:
        conn.execute(
            """
            UPDATE character_wardrobe_slots
            SET display_name = ?, updated_at = ?
            WHERE player_uuid = ? AND character_id = ? AND slot = ?
            """,
            (name, _iso_now(), uuid, cid, slot_key),
        )
        conn.commit()
    return get_wardrobe(uuid, cid)


def ack_wardrobe_slots(
    player_uuid: str, character_id: str, slots: list[str]
) -> dict[str, Any]:
    """Clear apply_pending for slots the plugin has pulled and applied."""
    roster = _require_owned_character(player_uuid, character_id)
    uuid = str(roster["player_uuid"])
    cid = str(roster["character_id"])
    clean: list[str] = []
    for raw in slots:
        try:
            clean.append(_normalize_slot(raw))
        except WardrobeError:
            continue
    if not clean:
        return get_wardrobe_for_plugin(uuid, cid)
    placeholders = ",".join("?" for _ in clean)
    with connect() as conn:
        conn.execute(
            f"""
            UPDATE character_wardrobe_slots
            SET apply_pending = 0
            WHERE player_uuid = ? AND character_id = ?
              AND slot IN ({placeholders})
            """,
            (uuid, cid, *clean),
        )
        conn.commit()
    return get_wardrobe_for_plugin(uuid, cid)


def clear_slot(
    player_uuid: str, character_id: str, slot: str
) -> dict[str, Any]:
    roster = _require_owned_character(player_uuid, character_id)
    uuid = str(roster["player_uuid"])
    cid = str(roster["character_id"])
    slot_key = _normalize_slot(slot)
    slots = _load_slots(uuid, cid)
    row = slots.get(slot_key)
    if row:
        _delete_png(row.get("png_relpath"))
        with connect() as conn:
            conn.execute(
                """
                DELETE FROM character_wardrobe_slots
                WHERE player_uuid = ? AND character_id = ? AND slot = ?
                """,
                (uuid, cid, slot_key),
            )
            conn.commit()
    active = roster.get("wardrobe_active_slot")
    if active and str(active).strip().lower() == slot_key:
        remaining = _load_slots(uuid, cid)
        swappable = swappable_slot_count(uuid)
        _normalize_active(uuid, cid, slot_key, remaining, swappable)
    return get_wardrobe(uuid, cid)


def set_active_slot(
    player_uuid: str, character_id: str, slot: str | None
) -> dict[str, Any]:
    return _set_active_slot(
        player_uuid, character_id, slot, include_textures=False
    )


def set_active_slot_for_plugin(
    player_uuid: str, character_id: str, slot: str | None
) -> dict[str, Any]:
    return _set_active_slot(
        player_uuid, character_id, slot, include_textures=True
    )


def _set_active_slot(
    player_uuid: str,
    character_id: str,
    slot: str | None,
    *,
    include_textures: bool,
) -> dict[str, Any]:
    roster = _require_owned_character(player_uuid, character_id)
    uuid = str(roster["player_uuid"])
    cid = str(roster["character_id"])
    swappable = swappable_slot_count(uuid)
    slots = _load_slots(uuid, cid)

    if slot is None or (isinstance(slot, str) and not slot.strip()):
        _set_active(uuid, cid, None)
        return _build_wardrobe_payload(
            uuid, cid, include_textures=include_textures
        )

    slot_key = (slot or "").strip().lower()
    if slot_key == "masked":
        raise WardrobeError(
            "Masked slot cannot be set as active",
            status_code=400,
        )
    if slot_key not in SWAPPABLE_SLOTS:
        raise WardrobeError(
            f"Invalid active slot (expected one of: {', '.join(sorted(SWAPPABLE_SLOTS))})",
            status_code=400,
        )
    if not _slot_unlocked(slot_key, swappable):
        raise WardrobeError("Slot locked for your rank", status_code=403)
    row = slots.get(slot_key)
    if not row or not row.get("png_relpath"):
        raise WardrobeError("Slot is empty", status_code=400)
    _set_active(uuid, cid, slot_key)
    return _build_wardrobe_payload(
        uuid, cid, include_textures=include_textures
    )


def resolve_slot_texture_path(
    player_uuid: str, character_id: str, slot: str
) -> Path:
    roster = _require_owned_character(player_uuid, character_id)
    uuid = str(roster["player_uuid"])
    cid = str(roster["character_id"])
    slot_key = _normalize_slot(slot)
    row = _load_slots(uuid, cid).get(slot_key)
    if not row:
        raise WardrobeError("Slot is empty", status_code=404)
    path = _png_abspath(row.get("png_relpath"))
    if path is None:
        raise WardrobeError("Slot texture missing", status_code=404)
    return path


def _pending_relpath(create_id: str, slot: str) -> str:
    return f"wardrobe/pending/{create_id}/{slot}.png"


def _require_pending_create(player_uuid: str, create_id: str) -> dict[str, Any]:
    uuid = (player_uuid or "").strip()
    cid = (create_id or "").strip()
    if not uuid or not cid:
        raise WardrobeError("player_uuid and create_id are required", status_code=400)
    with connect() as conn:
        row = conn.execute(
            """
            SELECT id, player_uuid, status, character_id
            FROM character_creates
            WHERE id = ? AND player_uuid = ?
            """,
            (cid, uuid),
        ).fetchone()
    if row is None:
        raise WardrobeError("Create not found", status_code=404)
    if str(row["status"] or "").strip().lower() != "pending":
        raise WardrobeError(
            "Create is not pending; wardrobe uploads locked",
            status_code=409,
        )
    return dict(row)


def upload_pending_create_wardrobe(
    player_uuid: str,
    create_id: str,
    slot: str,
    png_bytes: bytes,
    *,
    display_name: str | None = None,
) -> dict[str, Any]:
    """Sign + store a wardrobe slot against a pending create (pre-roster)."""
    create = _require_pending_create(player_uuid, create_id)
    uuid = str(create["player_uuid"])
    cid = str(create["id"])
    slot_key = _normalize_slot(slot)
    swappable = swappable_slot_count(uuid)
    if not _slot_unlocked(slot_key, swappable):
        raise WardrobeError("Slot locked for your rank", status_code=403)
    try:
        validate_png(png_bytes, WARDROBE_PNG_SIZE)
    except StorageError as e:
        raise WardrobeError(str(e), status_code=400) from e
    model = detect_skin_model(png_bytes)
    texture_value, texture_signature = sign_wardrobe_skin(png_bytes, model)
    name = _normalize_display_name(display_name)

    with connect() as conn:
        existing = conn.execute(
            """
            SELECT png_relpath, display_name FROM character_create_wardrobe
            WHERE create_id = ? AND slot = ?
            """,
            (cid, slot_key),
        ).fetchone()
    keep_name = (
        name
        if display_name is not None
        else (
            str(existing["display_name"] or "").strip() or None
            if existing
            else None
        )
    )
    if existing:
        _delete_png(existing["png_relpath"] if existing else None)

    rel = _pending_relpath(cid, slot_key)
    out = DATA_DIR / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(png_bytes)
    now = _iso_now()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO character_create_wardrobe (
                create_id, slot, png_relpath,
                texture_value, texture_signature, model,
                display_name, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(create_id, slot) DO UPDATE SET
                png_relpath = excluded.png_relpath,
                texture_value = excluded.texture_value,
                texture_signature = excluded.texture_signature,
                model = excluded.model,
                display_name = excluded.display_name,
                updated_at = excluded.updated_at
            """,
            (
                cid,
                slot_key,
                rel,
                texture_value,
                texture_signature,
                model,
                keep_name,
                now,
            ),
        )
        conn.commit()
    return {
        "ok": True,
        "create_id": cid,
        "slot": slot_key,
        "model": model,
        "display_name": _effective_display_name(
            slot_key, {"display_name": keep_name}
        ),
        "signed": True,
    }


def clear_pending_create_wardrobe(
    player_uuid: str, create_id: str, slot: str
) -> dict[str, Any]:
    create = _require_pending_create(player_uuid, create_id)
    cid = str(create["id"])
    slot_key = _normalize_slot(slot)
    with connect() as conn:
        row = conn.execute(
            """
            SELECT png_relpath FROM character_create_wardrobe
            WHERE create_id = ? AND slot = ?
            """,
            (cid, slot_key),
        ).fetchone()
        if row:
            _delete_png(row["png_relpath"])
            conn.execute(
                """
                DELETE FROM character_create_wardrobe
                WHERE create_id = ? AND slot = ?
                """,
                (cid, slot_key),
            )
            conn.commit()
    return {"ok": True, "create_id": cid, "slot": slot_key, "cleared": True}


def flush_pending_wardrobe(
    player_uuid: str, create_id: str, character_id: str
) -> int:
    """Move pending create wardrobe slots onto the live character. Returns count."""
    uuid = (player_uuid or "").strip()
    create_key = (create_id or "").strip()
    char_id = (character_id or "").strip()
    if not uuid or not create_key or not char_id:
        return 0
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT slot, png_relpath, texture_value, texture_signature,
                   model, display_name
            FROM character_create_wardrobe
            WHERE create_id = ?
            """,
            (create_key,),
        ).fetchall()
    if not rows:
        return 0

    flushed = 0
    now = _iso_now()
    for row in rows:
        slot_key = str(row["slot"])
        src = _png_abspath(row["png_relpath"])
        if src is None or not src.is_file():
            continue
        png_bytes = src.read_bytes()
        rel = _slot_relpath(uuid, char_id, slot_key)
        dest = DATA_DIR / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(png_bytes)
        custom_name = str(row["display_name"] or "").strip() or None
        with connect() as conn:
            conn.execute(
                """
                INSERT INTO character_wardrobe_slots (
                    player_uuid, character_id, slot, png_relpath,
                    texture_value, texture_signature, model,
                    display_name, apply_pending, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
                ON CONFLICT(player_uuid, character_id, slot) DO UPDATE SET
                    png_relpath = excluded.png_relpath,
                    texture_value = excluded.texture_value,
                    texture_signature = excluded.texture_signature,
                    model = excluded.model,
                    display_name = excluded.display_name,
                    apply_pending = 1,
                    updated_at = excluded.updated_at
                """,
                (
                    uuid,
                    char_id,
                    slot_key,
                    rel,
                    row["texture_value"],
                    row["texture_signature"],
                    row["model"],
                    custom_name,
                    now,
                ),
            )
            conn.commit()
        _delete_png(row["png_relpath"])
        flushed += 1

    with connect() as conn:
        conn.execute(
            "DELETE FROM character_create_wardrobe WHERE create_id = ?",
            (create_key,),
        )
        # Prefer base as active when present and roster row exists
        base = conn.execute(
            """
            SELECT 1 FROM character_wardrobe_slots
            WHERE player_uuid = ? AND character_id = ? AND slot = 'base'
              AND png_relpath IS NOT NULL
            """,
            (uuid, char_id),
        ).fetchone()
        if base is not None:
            roster = conn.execute(
                """
                SELECT 1 FROM character_roster
                WHERE player_uuid = ? AND character_id = ?
                """,
                (uuid, char_id),
            ).fetchone()
            if roster is not None:
                conn.execute(
                    """
                    UPDATE character_roster
                    SET wardrobe_active_slot = 'base'
                    WHERE player_uuid = ? AND character_id = ?
                      AND (wardrobe_active_slot IS NULL OR wardrobe_active_slot = '')
                    """,
                    (uuid, char_id),
                )
        conn.commit()
    return flushed
