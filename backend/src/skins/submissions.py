"""Create and fetch skins submissions."""

from __future__ import annotations

import json
import re
import shutil
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .db import SKINS_DIR, connect
from .discord_link import get_link_for_uuid
from .naming import (
    BOW_FRAME_FIELDS,
    CROSSBOW_FRAME_FIELDS,
    SlugError,
    base_id_from_slug,
    prefix_slug,
    resolve_submission_slug,
)
from .notifications import enqueue_submitted
from .storage import (
    ARMOR_FIELDS,
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


def _validate_name_colours(raw: list[str] | None, *, add_name: bool) -> list[str]:
    if not add_name:
        return []
    if not raw:
        return []
    out: list[str] = []
    for item in raw:
        out.append(_normalize_colour_token(str(item)))
    if len(out) > 8:
        raise SubmissionError("at most 8 name colours")
    return out


def _validate_name_styles(raw: list[str] | None, *, add_name: bool) -> list[str]:
    if not add_name:
        return []
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
    player_key = None
    link = get_link_for_uuid(row["player_uuid"])
    if link:
        player_key = link.get("player_key")
    return {
        "id": row["id"],
        "kind": row["kind"],
        "slug": row["slug"],
        "display_name": row["display_name"],
        "grip_preset": row["grip_preset"],
        "base_set": _row_base_set(row),
        "add_name": _row_add_name(row),
        "name_colours": _row_json_list(row, "name_colours"),
        "name_styles": _row_json_list(row, "name_styles"),
        "player_key": player_key,
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
        "player_key": link.get("player_key"),
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


def slug_taken(slug: str) -> bool:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT 1 FROM submissions
            WHERE slug = ? AND status IN (?, ?, ?)
            LIMIT 1
            """,
            (slug, *ACTIVE_STATUSES),
        ).fetchone()
    return row is not None


def check_player_conflicts(
    player_uuid: str,
    *,
    display_name: str | None = None,
    base_id: str | None = None,
) -> dict:
    """Return conflicts for same-player active display_name and/or base_id."""
    uuid = (player_uuid or "").strip()
    display = (display_name or "").strip()
    base = (base_id or "").strip() or None
    conflicts: list[dict] = []
    if not uuid:
        return {"ok": True, "conflicts": conflicts}

    link = get_link_for_uuid(uuid) or {}
    player_key = link.get("player_key")

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
        if display and str(row["display_name"]).strip().lower() == display.lower():
            reasons.append("display_name")
        row_base = base_id_from_slug(str(row["slug"]), player_key)
        if base and row_base == base:
            reasons.append("base_id")
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
    slug: str | None = None,
    filenames: dict[str, str | None] | None = None,
    add_name: bool = False,
    name_colours: list[str] | None = None,
    name_styles: list[str] | None = None,
) -> dict:
    kind = (kind or "").strip()
    if kind == "item":
        raise SubmissionError("kind 'item' is disabled")
    if kind not in ALLOWED_KINDS:
        raise SubmissionError(
            "kind must be armor_set, handheld, large_handheld, "
            "bow, large_bow, or crossbow"
        )

    base = _validate_base_set(kind, base_set)

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
    colours = _validate_name_colours(name_colours, add_name=want_add_name)
    styles = _validate_name_styles(name_styles, add_name=want_add_name)
    colours_json = json.dumps(colours) if colours else None
    styles_json = json.dumps(styles) if styles else None

    if kind == "armor_set":
        missing = [f for f in ARMOR_FIELDS if f not in files_bytes]
        if missing:
            raise SubmissionError(f"Missing files: {', '.join(missing)}")
    elif kind in BOW_KINDS:
        missing = [f for f in BOW_FRAME_FIELDS if f not in files_bytes]
        if missing:
            raise SubmissionError(f"Missing files: {', '.join(missing)}")
    elif kind in CROSSBOW_KINDS:
        missing = [f for f in CROSSBOW_FRAME_FIELDS if f not in files_bytes]
        if missing:
            raise SubmissionError(f"Missing files: {', '.join(missing)}")
    elif "texture" not in files_bytes:
        raise SubmissionError("Missing file: texture")

    names = filenames or {}
    try:
        base_id = resolve_submission_slug(kind, names, provided_slug=slug)
    except SlugError:
        raise

    player_uuid = session_row["player_uuid"]
    link = get_link_for_uuid(player_uuid)
    if not link or not link.get("discord_user_id"):
        raise SubmissionError(
            "Link Discord in-game with /linkdiscord first"
        )
    player_key = link.get("player_key")
    if not player_key:
        raise SubmissionError(
            "Player key missing — re-link Discord or wait for API migrate"
        )

    try:
        full_slug = prefix_slug(player_key, base_id)
    except SlugError:
        raise

    conflict = check_player_conflicts(
        player_uuid, display_name=display, base_id=base_id
    )
    if not conflict["ok"]:
        reasons = set()
        for c in conflict["conflicts"]:
            reasons.update(c.get("reasons") or [])
        if "display_name" in reasons and "base_id" in reasons:
            msg = (
                "You already have an active skin with this item name "
                "and file id. Delete it in-game or choose a different name/files."
            )
        elif "display_name" in reasons:
            msg = (
                "You already have an active skin named "
                f"'{display}'. Choose a different item name "
                "or ask staff to delete the old one."
            )
        else:
            msg = (
                f"You already have an active skin with file id '{base_id}'. "
                "Rename your PNG(s) or ask staff to delete the old one."
            )
        raise SubmissionError(msg)

    if slug_taken(full_slug):
        raise SlugConflictError(
            f"A skin with file id '{full_slug}' is already in use. "
            "Rename your PNG(s) and try again."
        )

    submission_id = str(uuid.uuid4())
    dir_path = f"skins/{submission_id}"
    created_at = _iso_now()
    code_id = session_row["code_id"]
    discord_id = str(link["discord_user_id"])
    slug = full_slug

    with connect() as conn:
        conn.execute(
            """
            INSERT INTO submissions (
                id, player_uuid, code_id, kind, slug, display_name,
                grip_preset, base_set, add_name, name_colours, name_styles,
                status, deny_reason, dir_path,
                created_at, reviewed_at, applied_at, discord_message_id,
                discord_user_id
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', NULL, ?, ?,
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
            add_name=want_add_name,
            name_colours=colours,
            name_styles=styles,
        )
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
    return sorted(p.name for p in out_dir.glob("*.png") if p.is_file())


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
                "player_key": names.get("player_key"),
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
                "add_name": _row_add_name(row),
                "name_colours": _row_json_list(row, "name_colours"),
                "name_styles": _row_json_list(row, "name_styles"),
                "player_key": names.get("player_key"),
                "reviewed_at": row["reviewed_at"],
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
        "player_key": names.get("player_key"),
        "minecraft_name": names.get("minecraft_name"),
    }


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
