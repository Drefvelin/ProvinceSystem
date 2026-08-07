"""Create and fetch skins submissions."""

from __future__ import annotations

import shutil
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .db import SKINS_DIR, connect
from .naming import SlugError, assert_slug
from .storage import ARMOR_FIELDS, StorageError, write_submission_files

ACTIVE_STATUSES = ("pending", "approved", "applied")
ALLOWED_KINDS = frozenset(
    {"armor_set", "item", "handheld", "large_handheld"}
)
GRIP_PRESETS = frozenset({"bottom", "middle", "top"})
MAX_DISPLAY_NAME = 80


class SubmissionError(ValueError):
    """Business-rule failure for submissions (not auth)."""


class SlugConflictError(SubmissionError):
    """Slug already used by an active submission."""


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _public_row(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "kind": row["kind"],
        "slug": row["slug"],
        "display_name": row["display_name"],
        "grip_preset": row["grip_preset"],
        "status": row["status"],
        "deny_reason": row["deny_reason"],
        "created_at": row["created_at"],
        "reviewed_at": row["reviewed_at"],
        "applied_at": row["applied_at"],
    }


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


def create_submission(
    session_row: sqlite3.Row,
    kind: str,
    slug: str,
    display_name: str,
    files_bytes: dict[str, bytes],
    grip_preset: str | None = None,
) -> dict:
    kind = (kind or "").strip()
    if kind not in ALLOWED_KINDS:
        raise SubmissionError(
            "kind must be armor_set, item, handheld, or large_handheld"
        )

    display = (display_name or "").strip()
    if not display:
        raise SubmissionError("display_name is required")
    if len(display) > MAX_DISPLAY_NAME:
        raise SubmissionError(f"display_name max length is {MAX_DISPLAY_NAME}")

    grip = (grip_preset or "").strip() or None
    if kind == "large_handheld":
        if grip not in GRIP_PRESETS:
            raise SubmissionError(
                "large_handheld requires grip_preset: bottom, middle, or top"
            )
    elif grip is not None:
        raise SubmissionError("grip_preset is only allowed for large_handheld")

    try:
        slug = assert_slug(slug)
    except SlugError:
        raise

    if slug_taken(slug):
        raise SlugConflictError(f"Slug '{slug}' is already in use")

    if kind == "armor_set":
        missing = [f for f in ARMOR_FIELDS if f not in files_bytes]
        if missing:
            raise SubmissionError(f"Missing files: {', '.join(missing)}")
    elif "texture" not in files_bytes:
        raise SubmissionError("Missing file: texture")

    submission_id = str(uuid.uuid4())
    dir_path = f"skins/{submission_id}"
    created_at = _iso_now()
    code_id = session_row["code_id"]
    player_uuid = session_row["player_uuid"]

    with connect() as conn:
        conn.execute(
            """
            INSERT INTO submissions (
                id, player_uuid, code_id, kind, slug, display_name,
                grip_preset, status, deny_reason, dir_path, created_at,
                reviewed_at, applied_at, discord_message_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', NULL, ?, ?, NULL, NULL, NULL)
            """,
            (
                submission_id,
                player_uuid,
                code_id,
                kind,
                slug,
                display,
                grip,
                dir_path,
                created_at,
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
        )
    except StorageError:
        _rollback_submission(submission_id)
        raise
    except Exception:
        _rollback_submission(submission_id)
        raise

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
        result.append(
            {
                "id": row["id"],
                "player_uuid": row["player_uuid"],
                "slug": row["slug"],
                "kind": row["kind"],
                "display_name": row["display_name"],
                "grip_preset": row["grip_preset"],
                "reviewed_at": row["reviewed_at"],
                "files": _list_png_files(row["id"]),
            }
        )
    return result


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
