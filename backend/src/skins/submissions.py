"""Create and fetch skins submissions."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .db import SKINS_DIR, connect
from .discord_link import get_link_for_uuid
from .naming import (
    ARMOR_FIELDS,
    ARMOR_TIER_LABELS,
    ARMOR_TIERS,
    BOW_FRAME_FIELDS,
    CROSSBOW_FRAME_FIELDS,
    MAX_TIER_ALIAS_LEN,
    SlugError,
    build_submission_id,
    sanitize_ign,
    slugify_display_name,
)
from .notifications import enqueue_submitted
from .name_preview import write_name_preview
from .storage import (
    BOW_KINDS,
    CROSSBOW_KINDS,
    StorageError,
    write_submission_files,
)

ACTIVE_STATUSES = ("pending", "approved", "applied")
ALLOWED_STYLES = frozenset(
    {"bold", "italic", "underline", "underlined", "strikethrough", "strike"}
)
_HEX_RE = re.compile(r"^#?[0-9A-Fa-f]{6}$")
_LEGACY_RE = re.compile(r"^[\u00a7&]?[0-9A-Fa-fk-or]$")
ALLOWED_KINDS = frozenset(
    {
        "armor_set",
        "handheld",
        "large_handheld",
        "bow",
        "large_bow",
        "crossbow",
    }
)
BASE_SETS: dict[str, frozenset[str]] = {
    "armor_set": frozenset(
        {"iron", "steel", "abyssalite", "mythril", "mage", "infantry"}
    ),
    "handheld": frozenset(
        {
            "swords",
            "battleaxes",
            "daggers",
            "warhammers",
            "shortswords",
            "hatchets",
            "hoes",
            "knives",
        }
    ),
    "large_handheld": frozenset(
        {"spears", "polearms", "greathammers", "staffs"}
    ),
    "bow": frozenset({"shortbows"}),
    "large_bow": frozenset({"longbows"}),
    "crossbow": frozenset({"crossbows"}),
}
GRIP_PRESETS = frozenset({"bottom", "middle", "top"})
MAX_DISPLAY_NAME = 80


class SubmissionError(ValueError):
    """Business-rule failure for submissions (not auth)."""


class SlugConflictError(SubmissionError):
    """Skin id already used by an active submission."""


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _row_base_set(row: sqlite3.Row) -> str | None:
    if "base_set" not in row.keys():
        return None
    return row["base_set"]


def _row_json_list(row: sqlite3.Row, key: str) -> list[str]:
    if key not in row.keys():
        return []
    raw = row[key]
    if raw is None or raw == "":
        return []
    if isinstance(raw, list):
        return [str(x) for x in raw]
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []
    if not isinstance(data, list):
        return []
    return [str(x) for x in data if x is not None and str(x).strip()]


def _row_json_object(row: sqlite3.Row, key: str) -> dict[str, str]:
    if key not in row.keys():
        return {}
    raw = row[key]
    if raw is None or raw == "":
        return {}
    if isinstance(raw, dict):
        return {str(k): str(v) for k, v in raw.items() if v is not None}
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {
        str(k): str(v)
        for k, v in data.items()
        if v is not None and str(v).strip()
    }


def _row_add_name(row: sqlite3.Row) -> bool:
    if "add_name" not in row.keys():
        return False
    return bool(row["add_name"])


def _normalize_colour_token(token: str) -> str:
    t = (token or "").strip()
    if not t:
        raise SubmissionError("empty colour token")
    if _HEX_RE.match(t):
        h = t if t.startswith("#") else f"#{t}"
        return h.lower()
    # normalize &c → §c for storage consistency
    if t.startswith("&") and len(t) == 2:
        t = "\u00a7" + t[1]
    if _LEGACY_RE.match(t) or (len(t) == 2 and t[0] in ("\u00a7", "&")):
        return "\u00a7" + t[-1].lower()
    raise SubmissionError(f"invalid colour '{token}' (use #RRGGBB or §c)")


def _validate_name_colours(raw: list[str] | None) -> list[str]:
    """Colours are independent of add_name (SkinSet display vs apply-name)."""
    if not raw:
        return []
    out: list[str] = []
    for item in raw:
        out.append(_normalize_colour_token(str(item)))
    if len(out) > 8:
        raise SubmissionError("at most 8 name colours")
    return out


def _validate_name_styles(raw: list[str] | None) -> list[str]:
    """Styles are independent of add_name."""
    if not raw:
        return []
    out: list[str] = []
    for item in raw:
        s = str(item).strip().lower()
        if s not in ALLOWED_STYLES:
            raise SubmissionError(f"invalid name style '{item}'")
        if s == "underlined":
            s = "underline"
        if s == "strike":
            s = "strikethrough"
        if s not in out:
            out.append(s)
    return out


def _public_row(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "kind": row["kind"],
        "slug": row["slug"],
        "display_name": row["display_name"],
        "grip_preset": row["grip_preset"],
        "base_set": _row_base_set(row),
        "tiers": _row_json_list(row, "tiers"),
        "tier_aliases": _row_json_object(row, "tier_aliases"),
        "add_name": _row_add_name(row),
        "name_colours": _row_json_list(row, "name_colours"),
        "name_styles": _row_json_list(row, "name_styles"),
        "status": row["status"],
        "deny_reason": row["deny_reason"],
        "created_at": row["created_at"],
        "reviewed_at": row["reviewed_at"],
        "applied_at": row["applied_at"],
        "discord_user_id": row["discord_user_id"]
        if "discord_user_id" in row.keys()
        else None,
    }


def _link_names(player_uuid: str) -> dict:
    link = get_link_for_uuid(player_uuid) or {}
    return {
        "minecraft_name": link.get("minecraft_name"),
        "discord_username": link.get("discord_username"),
        "discord_user_id": link.get("discord_user_id"),
    }


def _validate_base_set(kind: str, base_set: str | None) -> str:
    raw = (base_set or "").strip()
    if not raw:
        raise SubmissionError("base_set is required")
    allowed = BASE_SETS.get(kind)
    if allowed is None or raw not in allowed:
        raise SubmissionError(
            f"base_set '{raw}' is not valid for kind '{kind}'"
        )
    return raw


def _validate_tiers(raw: list[str] | None) -> list[str]:
    if not raw:
        raise SubmissionError("armor_set requires 1–6 tiers")
    if len(raw) > 6:
        raise SubmissionError("at most 6 armor tiers")
    out: list[str] = []
    seen: set[str] = set()
    tier_names = ", ".join(sorted(ARMOR_TIERS))
    for item in raw:
        tier = (item or "").strip().lower()
        if not tier:
            raise SubmissionError("empty tier name")
        if tier not in ARMOR_TIERS:
            raise SubmissionError(
                f"tier '{tier}' is not valid (must be one of: {tier_names})"
            )
        if tier in seen:
            raise SubmissionError(f"duplicate tier '{tier}'")
        seen.add(tier)
        out.append(tier)
    return out


def _validate_tier_aliases(
    tiers: list[str], raw: dict[str, str] | None
) -> dict[str, str]:
    """Per-tier display suffix. Missing → default Iron/Steel/… labels."""
    incoming: dict[str, str] = {}
    if raw:
        for key, value in raw.items():
            tier = str(key).strip().lower()
            if tier not in tiers:
                raise SubmissionError(
                    f"tier_aliases key '{key}' is not in this submission's tiers"
                )
            alias = str(value or "").strip()
            if not alias:
                continue
            if len(alias) > MAX_TIER_ALIAS_LEN:
                raise SubmissionError(
                    f"tier alias for '{tier}' max length is {MAX_TIER_ALIAS_LEN}"
                )
            incoming[tier] = alias
    out: dict[str, str] = {}
    for tier in tiers:
        out[tier] = incoming.get(tier) or ARMOR_TIER_LABELS.get(
            tier, tier.capitalize()
        )
    return out


def _reject_duplicate_textures(files_bytes: dict[str, bytes]) -> None:
    """Every uploaded PNG in a submission must have unique bytes."""
    if len(files_bytes) < 2:
        return
    seen: dict[str, str] = {}
    for field, data in files_bytes.items():
        dig = hashlib.sha256(data).hexdigest()
        if dig in seen:
            raise SubmissionError(
                f"File '{field}' is identical to '{seen[dig]}' — "
                "each PNG in a submission must be unique"
            )
        seen[dig] = field


def slug_taken(slug: str) -> bool:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT 1 FROM submissions
            WHERE id = ? AND status IN (?, ?, ?)
            LIMIT 1
            """,
            (slug, *ACTIVE_STATUSES),
        ).fetchone()
    return row is not None


def check_player_conflicts(
    player_uuid: str,
    *,
    display_name: str | None = None,
    submission_id: str | None = None,
) -> dict:
    """Return conflicts for same-player active display_name and/or submission id."""
    uuid = (player_uuid or "").strip()
    display = (display_name or "").strip()
    sid = (submission_id or "").strip() or None
    conflicts: list[dict] = []
    if not uuid:
        return {"ok": True, "conflicts": conflicts}

    if sid is None and display:
        link = get_link_for_uuid(uuid) or {}
        minecraft_name = link.get("minecraft_name")
        if minecraft_name:
            try:
                sid = build_submission_id(minecraft_name, display)
            except SlugError:
                pass

    with connect() as conn:
        rows = conn.execute(
            """
            SELECT id, slug, display_name, status, kind
            FROM submissions
            WHERE player_uuid = ? AND status IN (?, ?, ?)
            """,
            (uuid, *ACTIVE_STATUSES),
        ).fetchall()

    for row in rows:
        reasons: list[str] = []
        row_display = str(row["display_name"]).strip()
        if display and row_display.lower() == display.lower():
            reasons.append("display_name")
        elif display:
            try:
                new_slug = slugify_display_name(display)
                row_slug = slugify_display_name(row_display)
                if new_slug.lower() == row_slug.lower():
                    reasons.append("display_name")
            except SlugError:
                pass
        row_id = str(row["id"])
        if sid and row_id == sid:
            reasons.append("id")
        if reasons:
            conflicts.append(
                {
                    "id": row["id"],
                    "slug": row["slug"],
                    "display_name": row["display_name"],
                    "status": row["status"],
                    "kind": row["kind"],
                    "reasons": reasons,
                }
            )
    return {"ok": len(conflicts) == 0, "conflicts": conflicts}


def create_submission(
    session_row: sqlite3.Row,
    kind: str,
    display_name: str,
    files_bytes: dict[str, bytes],
    grip_preset: str | None = None,
    base_set: str | None = None,
    *,
    tiers: list[str] | None = None,
    tier_aliases: dict[str, str] | None = None,
    filenames: dict[str, str | None] | None = None,
    add_name: bool = False,
    name_colours: list[str] | None = None,
    name_styles: list[str] | None = None,
) -> dict:
    _ = filenames  # upload names ignored for identity

    kind = (kind or "").strip()
    if kind == "item":
        raise SubmissionError("kind 'item' is disabled")
    if kind not in ALLOWED_KINDS:
        raise SubmissionError(
            "kind must be armor_set, handheld, large_handheld, "
            "bow, large_bow, or crossbow"
        )

    display = (display_name or "").strip()
    if not display:
        raise SubmissionError("Item name is required")
    if len(display) > MAX_DISPLAY_NAME:
        raise SubmissionError(f"Item name max length is {MAX_DISPLAY_NAME}")

    grip = (grip_preset or "").strip() or None
    if kind == "large_handheld":
        if grip not in GRIP_PRESETS:
            raise SubmissionError(
                "large_handheld requires grip_preset: bottom, middle, or top"
            )
    elif grip is not None:
        raise SubmissionError("grip_preset is only allowed for large_handheld")

    want_add_name = bool(add_name)
    colours = _validate_name_colours(name_colours)
    styles = _validate_name_styles(name_styles)
    colours_json = json.dumps(colours) if colours else None
    styles_json = json.dumps(styles) if styles else None

    tier_list: list[str] | None
    aliases: dict[str, str] | None
    if kind == "armor_set":
        tier_list = _validate_tiers(tiers)
        aliases = _validate_tier_aliases(tier_list, tier_aliases)
        base: str | None = None
        for tier in tier_list:
            missing = [
                f"{tier}_{field}"
                for field in ARMOR_FIELDS
                if f"{tier}_{field}" not in files_bytes
            ]
            if missing:
                raise SubmissionError(f"Missing files: {', '.join(missing)}")
    else:
        if tiers:
            raise SubmissionError("tiers are only allowed for armor_set")
        if tier_aliases:
            raise SubmissionError("tier_aliases are only allowed for armor_set")
        tier_list = None
        aliases = None
        base = _validate_base_set(kind, base_set)
        if kind in BOW_KINDS:
            missing = [f for f in BOW_FRAME_FIELDS if f not in files_bytes]
            if missing:
                raise SubmissionError(f"Missing files: {', '.join(missing)}")
        elif kind in CROSSBOW_KINDS:
            missing = [
                f for f in CROSSBOW_FRAME_FIELDS if f not in files_bytes
            ]
            if missing:
                raise SubmissionError(f"Missing files: {', '.join(missing)}")
        elif "texture" not in files_bytes:
            raise SubmissionError("Missing file: texture")

    _reject_duplicate_textures(files_bytes)

    player_uuid = session_row["player_uuid"]
    link = get_link_for_uuid(player_uuid)
    if not link or not link.get("discord_user_id"):
        raise SubmissionError(
            "Link Discord in-game with /linkdiscord first"
        )
    minecraft_name = link.get("minecraft_name")
    if not minecraft_name:
        raise SubmissionError(
            "Minecraft name missing — re-link Discord or wait for API migrate"
        )

    try:
        submission_id = build_submission_id(minecraft_name, display)
    except SlugError:
        raise

    slug = submission_id

    conflict = check_player_conflicts(
        player_uuid, display_name=display, submission_id=submission_id
    )
    if not conflict["ok"]:
        reasons = set()
        for c in conflict["conflicts"]:
            reasons.update(c.get("reasons") or [])
        if "display_name" in reasons and "id" in reasons:
            msg = (
                "You already have an active skin with this item name "
                "and id. Delete it in-game or choose a different item name."
            )
        elif "display_name" in reasons:
            msg = (
                "You already have an active skin named "
                f"'{display}'. Choose a different item name "
                "or ask staff to delete the old one."
            )
        else:
            msg = (
                f"You already have an active skin with id '{submission_id}'. "
                "Choose a different item name or ask staff to delete the old one."
            )
        raise SubmissionError(msg)

    if slug_taken(submission_id):
        raise SlugConflictError(
            f"A skin with id '{submission_id}' is already in use. "
            "Choose a different item name and try again."
        )

    tiers_json = json.dumps(tier_list) if tier_list else None
    aliases_json = json.dumps(aliases) if aliases else None
    dir_path = f"skins/{submission_id}"
    created_at = _iso_now()
    code_id = session_row["code_id"]
    discord_id = str(link["discord_user_id"])

    with connect() as conn:
        conn.execute(
            """
            INSERT INTO submissions (
                id, player_uuid, code_id, kind, slug, display_name,
                grip_preset, base_set, tiers, tier_aliases, add_name,
                name_colours, name_styles,
                status, deny_reason, dir_path,
                created_at, reviewed_at, applied_at, discord_message_id,
                discord_user_id
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', NULL, ?, ?,
                NULL, NULL, NULL, ?
            )
            """,
            (
                submission_id,
                player_uuid,
                code_id,
                kind,
                slug,
                display,
                grip,
                base,
                tiers_json,
                aliases_json,
                1 if want_add_name else 0,
                colours_json,
                styles_json,
                dir_path,
                created_at,
                discord_id,
            ),
        )
        conn.commit()

    try:
        write_submission_files(
            submission_id,
            slug,
            kind,
            display,
            files_bytes,
            grip_preset=grip,
            base_set=base,
            tiers=tier_list,
            tier_aliases=aliases,
            add_name=want_add_name,
            name_colours=colours,
            name_styles=styles,
        )
        write_name_preview(
            submission_id,
            display,
            name_colours=colours,
            name_styles=styles,
        )
        # review_sheet.png is composed on first GET (build_review_sheet) so the
        # upload response stays fast (multi-tier armor + SSH tunnels).
    except StorageError:
        _rollback_submission(submission_id)
        raise
    except Exception:
        _rollback_submission(submission_id)
        raise

    enqueue_submitted(
        submission_id,
        discord_id,
        display_name=display,
        kind=kind,
        slug=slug,
    )

    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM submissions WHERE id = ?",
            (submission_id,),
        ).fetchone()

    return _public_row(row)


def _rollback_submission(submission_id: str) -> None:
    with connect() as conn:
        conn.execute("DELETE FROM submissions WHERE id = ?", (submission_id,))
        conn.commit()
    out = SKINS_DIR / submission_id
    if out.exists():
        shutil.rmtree(out, ignore_errors=True)


def get_submission_for_owner(
    submission_id: str, player_uuid: str
) -> dict | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM submissions WHERE id = ?",
            (submission_id,),
        ).fetchone()
    if row is None or row["player_uuid"] != player_uuid:
        return None
    return _public_row(row)


def _get_row(submission_id: str) -> sqlite3.Row | None:
    with connect() as conn:
        return conn.execute(
            "SELECT * FROM submissions WHERE id = ?",
            (submission_id,),
        ).fetchone()


def _list_png_files(submission_id: str) -> list[str]:
    out_dir = SKINS_DIR / submission_id
    if not out_dir.is_dir():
        return []
    names = sorted(p.name for p in out_dir.glob("*.png") if p.is_file())
    preferred = []
    for key in ("review_sheet.png", "name_preview.png"):
        if key in names:
            preferred.append(key)
            names = [n for n in names if n != key]
    return preferred + names


def approve_submission(submission_id: str) -> dict:
    row = _get_row(submission_id)
    if row is None:
        raise SubmissionError("Submission not found")
    if row["status"] != "pending":
        raise SubmissionError("Only pending submissions can be approved")

    reviewed_at = _iso_now()
    with connect() as conn:
        conn.execute(
            """
            UPDATE submissions
            SET status = 'approved', reviewed_at = ?, deny_reason = NULL
            WHERE id = ?
            """,
            (reviewed_at, submission_id),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM submissions WHERE id = ?",
            (submission_id,),
        ).fetchone()
    return _public_row(row)


def deny_submission(submission_id: str, reason: str) -> dict:
    reason = (reason or "").strip()
    if not reason:
        raise SubmissionError("deny reason is required")

    row = _get_row(submission_id)
    if row is None:
        raise SubmissionError("Submission not found")
    if row["status"] != "pending":
        raise SubmissionError("Only pending submissions can be denied")

    reviewed_at = _iso_now()
    with connect() as conn:
        conn.execute(
            """
            UPDATE submissions
            SET status = 'denied', reviewed_at = ?, deny_reason = ?
            WHERE id = ?
            """,
            (reviewed_at, reason, submission_id),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM submissions WHERE id = ?",
            (submission_id,),
        ).fetchone()
    return _public_row(row)


def list_pending() -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM submissions
            WHERE status = 'pending'
            ORDER BY created_at ASC
            """
        ).fetchall()

    result = []
    for row in rows:
        names = _link_names(row["player_uuid"])
        result.append(
            {
                "id": row["id"],
                "player_uuid": row["player_uuid"],
                "slug": row["slug"],
                "kind": row["kind"],
                "display_name": row["display_name"],
                "grip_preset": row["grip_preset"],
                "base_set": _row_base_set(row),
                "tiers": _row_json_list(row, "tiers"),
                "tier_aliases": _row_json_object(row, "tier_aliases"),
                "add_name": _row_add_name(row),
                "name_colours": _row_json_list(row, "name_colours"),
                "name_styles": _row_json_list(row, "name_styles"),
                "created_at": row["created_at"],
                "discord_user_id": names.get("discord_user_id")
                or (
                    row["discord_user_id"]
                    if "discord_user_id" in row.keys()
                    else None
                ),
                "minecraft_name": names.get("minecraft_name"),
                "discord_username": names.get("discord_username"),
                "files": _list_png_files(row["id"]),
            }
        )
    return result


def list_approved_pending_apply(since: str | None = None) -> list[dict]:
    sql = """
        SELECT * FROM submissions
        WHERE status = 'approved' AND applied_at IS NULL
    """
    params: list = []
    if since:
        sql += " AND reviewed_at >= ?"
        params.append(since.strip())
    sql += " ORDER BY reviewed_at ASC"

    with connect() as conn:
        rows = conn.execute(sql, params).fetchall()

    result = []
    for row in rows:
        names = _link_names(row["player_uuid"])
        result.append(
            {
                "id": row["id"],
                "player_uuid": row["player_uuid"],
                "slug": row["slug"],
                "kind": row["kind"],
                "display_name": row["display_name"],
                "grip_preset": row["grip_preset"],
                "base_set": _row_base_set(row),
                "tiers": _row_json_list(row, "tiers"),
                "tier_aliases": _row_json_object(row, "tier_aliases"),
                "add_name": _row_add_name(row),
                "name_colours": _row_json_list(row, "name_colours"),
                "name_styles": _row_json_list(row, "name_styles"),
                "reviewed_at": row["reviewed_at"],
                "minecraft_name": names.get("minecraft_name"),
                "discord_username": names.get("discord_username"),
                "files": _list_png_files(row["id"]),
            }
        )
    return result


def get_submission_for_plugin(submission_id: str) -> dict | None:
    sid = (submission_id or "").strip()
    if not sid:
        return None
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM submissions WHERE id = ?",
            (sid,),
        ).fetchone()
    if row is None:
        return None
    names = _link_names(row["player_uuid"])
    return {
        "id": row["id"],
        "player_uuid": row["player_uuid"],
        "slug": row["slug"],
        "kind": row["kind"],
        "display_name": row["display_name"],
        "status": row["status"],
        "base_set": _row_base_set(row),
        "tiers": _row_json_list(row, "tiers"),
        "minecraft_name": names.get("minecraft_name"),
    }


def list_deletable_submissions() -> list[dict]:
    """Active submissions staff can delete (pending / approved / applied)."""
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT id, slug, display_name, kind, status, created_at
            FROM submissions
            WHERE status IN (?, ?, ?)
            ORDER BY created_at DESC
            """,
            ACTIVE_STATUSES,
        ).fetchall()
    return [
        {
            "id": row["id"],
            "slug": row["slug"],
            "display_name": row["display_name"],
            "kind": row["kind"],
            "status": row["status"],
        }
        for row in rows
    ]


def revoke_submission(submission_id: str) -> dict:
    """Mark submission revoked so slug can be reused and won't re-apply."""
    sid = (submission_id or "").strip()
    if not sid:
        raise SubmissionError("submission id is required")
    row = _get_row(sid)
    if row is None:
        raise SubmissionError("Submission not found")
    status = str(row["status"] or "")
    if status == "revoked":
        return {**_public_row(row), "already_revoked": True}
    if status == "denied":
        raise SubmissionError("Denied submissions cannot be revoked")

    reviewed_at = row["reviewed_at"] or _iso_now()
    with connect() as conn:
        conn.execute(
            """
            UPDATE submissions
            SET status = 'revoked', reviewed_at = COALESCE(reviewed_at, ?)
            WHERE id = ?
            """,
            (reviewed_at, sid),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM submissions WHERE id = ?",
            (sid,),
        ).fetchone()
    out = _public_row(row)
    out["revoked"] = True
    return out


def mark_applied(submission_ids: list[str]) -> list[str]:
    applied: list[str] = []
    now = _iso_now()
    with connect() as conn:
        for sid in submission_ids:
            sid = (sid or "").strip()
            if not sid:
                continue
            cur = conn.execute(
                """
                UPDATE submissions
                SET status = 'applied', applied_at = ?
                WHERE id = ? AND status = 'approved' AND applied_at IS NULL
                """,
                (now, sid),
            )
            if cur.rowcount:
                applied.append(sid)
        conn.commit()
    return applied


def resolve_submission_file(submission_id: str, filename: str) -> Path | None:
    name = (filename or "").strip()
    if not name or "/" in name or "\\" in name or name in (".", ".."):
        return None
    if ".." in name:
        return None

    base = (SKINS_DIR / submission_id).resolve()
    if not base.is_dir():
        return None

    candidate = (base / name).resolve()
    try:
        candidate.relative_to(base)
    except ValueError:
        return None

    if not candidate.is_file():
        return None
    return candidate
