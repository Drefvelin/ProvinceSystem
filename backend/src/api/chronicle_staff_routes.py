"""Staff-gated chronicle wipe / backup listing / restore.

The CLI (`python -m src.scripts.chronicle.wipe --map dev`) was protected by the
fact that it needed shell access on the server. These routes trade that for a
per-map staff permission, so two things stand in for the missing shell:

* a **typed confirmation** — the body must repeat the resolved map id exactly,
  so a stray fetch or a mis-clicked button cannot wipe a map; and
* an **audit row** — who, when, why, how many days and where the bytes went.

Neither is decoration. Do not relax them.

There is deliberately no "all maps" form: one request, one named map, always.
"""

from __future__ import annotations

import os
import time

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from .http_headers import add_no_cache
from .map_access import (
    ensure_map_staff_write,
    get_character_session,
    is_character_ui_dev,
)
from .request_body import read_json_body
from ..scripts.chronicle import audit
from ..scripts.chronicle.restore import (
    RestoreError,
    has_live_data,
    restore_wipe,
    validate_backup_path,
)
from ..scripts.chronicle.store import chronicle_lock_path
from ..scripts.chronicle.wipe import perform_wipe
from ..scripts.util.maplock import MapLockBusy, map_lock

chronicle_staff_router = APIRouter()

MAX_REASON_LENGTH = 500
BACKUP_LIST_LIMIT = 100

# These bodies are three short fields. The cap only exists so an unauthenticated
# or merely-curious caller cannot make the process buffer an arbitrary body
# before the gate's work is done.
MAX_STAFF_BODY_BYTES = 64 * 1024

_UI_DEV_ACTOR = "ui-dev"
_UNKNOWN_ACTOR = "unknown"

# One in-flight destructive chronicle operation per map. A wipe racing a restore
# (or another wipe) on the same map interleaves a directory move with a row
# delete, which is the one thing the crash ordering cannot make safe.
#
# This used to be a process-local `threading.Lock`, which is exactly nothing
# under more than one uvicorn worker: two wipes on the same map land on
# different workers, both acquire their own lock and both proceed. The lock in
# `scripts/util/maplock.py` is held against every process, including the
# `python -m src.scripts.chronicle.wipe` CLI, and captures take it too — see
# `capture.capture_if_due`, which every SF upload schedules as a background
# task and which used to be able to run straight through a wipe.
#
# It has to be acquired *inside* the threadpool call rather than around it: the
# lock is reentrant per thread (so `perform_wipe` can take it again), and
# `run_in_threadpool` runs the body on a different thread from the event loop.
_BUSY_DETAIL = "A chronicle wipe or restore is already running for '{map_id}'."


def _wipe_under_lock(map_id: str, actor: str, reason: str):
    """perform_wipe plus its audit row, as one uninterruptible unit."""
    with map_lock(chronicle_lock_path(map_id), blocking=False):
        result = perform_wipe(map_id)
        if not result.performed:
            return result, None
        wipe_id = audit.record_wipe(
            map_id,
            wiped_at=result.archived_at,
            wiped_by=actor,
            day_count=result.day_count,
            backup_path=result.backup_path,
            reason=reason,
        )
        return result, wipe_id


def _restore_under_lock(map_id: str, record: audit.WipeRecord, merge: bool, actor: str):
    """The live-data check, the restore and its audit row, as one unit.

    Returns None for the live-data refusal, so the route can answer 409 without
    the check and the restore it guards being two separately-decided things.
    """
    with map_lock(chronicle_lock_path(map_id), blocking=False):
        if not merge and has_live_data(map_id):
            return None
        result = restore_wipe(
            map_id,
            archived_at=record.wiped_at,
            backup_path=record.backup_path,
            merge=merge,
        )
        restored_at = int(time.time())
        audit.mark_restored(
            map_id,
            record.id,
            restored_at=restored_at,
            restored_by=actor,
        )
        return result, restored_at


def _staff_actor(authorization: str | None) -> str:
    """Identity to stamp on the audit row.

    `ensure_map_staff_write` has already decided this caller may proceed; this
    only names them. The dev bypass has no session at all, so it is recorded as
    what it is rather than being blamed on a real player.
    """
    session = get_character_session(authorization)
    if session is not None:
        actor = str(session.get("player_uuid") or "").strip()
        if actor:
            return actor
    if is_character_ui_dev():
        return _UI_DEV_ACTOR
    return _UNKNOWN_ACTOR


async def _json_body(request: Request) -> dict:
    """Bounded read, shared with the upload route.

    `request.json()` buffers an unbounded body and lets a `RecursionError` from
    a deeply nested one escape as a 500; `read_json_body` caps the bytes (413)
    and answers 400 for anything unparsable.
    """
    try:
        payload = await read_json_body(request, MAX_STAFF_BODY_BYTES)
    except HTTPException:
        raise
    except Exception as exc:  # malformed/absent body
        raise HTTPException(
            status_code=400, detail="A JSON object body is required"
        ) from exc
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="A JSON object body is required")
    return payload


def _backup_label(backup_path: str | None) -> str | None:
    """Basename of a backup directory — never the absolute server path.

    The client only ever needs `backup_id` to restore; the full path told a
    staff browser where the data directory lives on the server. The key stays
    present because the UI renders it.
    """
    if not backup_path:
        return None
    return os.path.basename(backup_path.rstrip("/\\")) or None


def _require_confirmation(payload: dict, map_id: str) -> None:
    """The body must echo the resolved map id, byte for byte.

    Compared against `entry.id` (the registry's normalised id), not the raw path
    segment, and with no case-folding or trimming: the point is that a human
    typed this map's name on purpose.
    """
    confirm = payload.get("confirm")
    if not isinstance(confirm, str) or confirm != map_id:
        raise HTTPException(
            status_code=400,
            detail=f"Confirmation must be exactly the map id '{map_id}'",
        )


def _require_reason(payload: dict) -> str:
    reason = payload.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        raise HTTPException(status_code=400, detail="A reason is required")
    cleaned = reason.strip()
    if len(cleaned) > MAX_REASON_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Reason must be {MAX_REASON_LENGTH} characters or fewer",
        )
    return cleaned


@chronicle_staff_router.post("/{map_name}/chronicle/wipe")
async def wipe_chronicle(
    map_name: str,
    request: Request,
    authorization: str | None = Header(default=None),
):
    """Archive and set aside one map's chronicle. Body: {confirm, reason}.

    `confirm` must equal the resolved map id exactly and `reason` must be
    non-empty; both are rejected with 400. Nothing is deleted — the day folders
    are renamed to `chronicle.bak.<stamp>` and the index rows are copied into
    the archive table first — and the whole operation is written to
    `map_chronicle_wipes` so it can be listed and undone.

    A map with no chronicle at all answers 200 with `performed: false` and
    writes no audit row: there is nothing to restore, and a phantom row would
    make the index report `last_wiped_at` for a map that was never captured.
    """
    entry = ensure_map_staff_write(map_name, authorization)
    map_id = entry.id  # never the raw path segment

    payload = await _json_body(request)
    _require_confirmation(payload, map_id)
    reason = _require_reason(payload)
    actor = _staff_actor(authorization)

    try:
        result, wipe_id = await run_in_threadpool(
            _wipe_under_lock, map_id, actor, reason
        )
    except MapLockBusy:
        raise HTTPException(
            status_code=429, detail=_BUSY_DETAIL.format(map_id=map_id)
        ) from None

    if not result.performed:
        return add_no_cache(
            JSONResponse(
                {
                    "ok": True,
                    "map": map_id,
                    "performed": False,
                    "wipe_id": None,
                    "day_count": 0,
                    "backup_path": None,
                    "wiped_at": None,
                    "wiped_by": actor,
                    "message": f"Nothing to wipe for map '{map_id}'.",
                }
            )
        )

    return add_no_cache(
        JSONResponse(
            {
                "ok": True,
                "map": map_id,
                "performed": True,
                "wipe_id": wipe_id,
                "day_count": result.day_count,
                "backup_path": _backup_label(result.backup_path),
                "wiped_at": result.archived_at,
                "wiped_by": actor,
                "reason": reason,
            }
        )
    )


@chronicle_staff_router.get("/{map_name}/chronicle/backups")
async def list_chronicle_backups(
    map_name: str,
    authorization: str | None = Header(default=None),
):
    """This map's wipe/restore history, newest first — the restore picker's data.

    Each entry: id, map_id, wiped_at (unix seconds, also the backup stamp),
    wiped_by, day_count, backup_path, reason, restored_at, restored_by,
    restored (bool) and backup_exists (whether the directory is still on disk).
    """
    entry = ensure_map_staff_write(map_name, authorization)
    map_id = entry.id

    records = await run_in_threadpool(audit.list_wipes, map_id, BACKUP_LIST_LIMIT)

    def _describe(record: audit.WipeRecord) -> dict:
        body = record.to_dict()
        body["backup_path"] = _backup_label(record.backup_path)
        body["backup_exists"] = _backup_exists(map_id, record.backup_path)
        return body

    def _describe_all() -> list[dict]:
        return [_describe(record) for record in records]

    # Up to BACKUP_LIST_LIMIT records, each costing a realpath + isdir stat
    # (_backup_exists) — real blocking syscalls that must not run on the event
    # loop, same as audit.list_wipes above.
    backups = await run_in_threadpool(_describe_all)

    return add_no_cache(
        JSONResponse(
            {
                "map": map_id,
                "backups": backups,
                "count": len(records),
            }
        )
    )


def _backup_exists(map_id: str, backup_path: str | None) -> bool:
    """Whether a listed backup is still on disk — path re-validated, never trusted."""
    if not backup_path:
        return False
    try:
        return os.path.isdir(validate_backup_path(map_id, backup_path))
    except (RestoreError, ValueError, OSError):
        return False


@chronicle_staff_router.post("/{map_name}/chronicle/restore")
async def restore_chronicle(
    map_name: str,
    request: Request,
    authorization: str | None = Header(default=None),
):
    """Put one wipe's days back. Body: {confirm, backup_id, merge?}.

    `confirm` must equal the resolved map id exactly (400 otherwise) and
    `backup_id` is the `id` of a row from GET /{map}/chronicle/backups; an id
    belonging to another map reads as 404, so a backup can never be restored
    across map boundaries.

    **Default is to refuse when live chronicle data exists** (409,
    `code: "live_data"`). Restoring on top of a live chronicle is the one path
    that can mix two different histories — days captured since the wipe, plus
    days from before it — and the map would look coherent while being neither.
    Refusing is recoverable (wipe again, then restore); a silent merge is not.
    Pass `merge: true` to opt in, and even then live days win: a day that
    already exists stays as it is, its backup copy is left in the backup
    directory and its name is reported in `skipped_days`. No live snapshot bytes
    are ever overwritten or deleted.

    The backup path from the audit row is re-derived and re-checked against this
    map's own output directory before anything is moved (400,
    `code: "bad_backup_path"`).
    """
    entry = ensure_map_staff_write(map_name, authorization)
    map_id = entry.id

    payload = await _json_body(request)
    _require_confirmation(payload, map_id)

    raw_id = payload.get("backup_id")
    if isinstance(raw_id, bool) or not isinstance(raw_id, int):
        try:
            backup_id = int(str(raw_id).strip())
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=400, detail="backup_id must be an integer"
            ) from None
    else:
        backup_id = raw_id

    merge = payload.get("merge")
    if merge is None:
        merge = False
    if not isinstance(merge, bool):
        raise HTTPException(status_code=400, detail="merge must be a boolean")

    actor = _staff_actor(authorization)

    record = await run_in_threadpool(audit.get_wipe, map_id, backup_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Backup not found for this map")

    try:
        outcome = await run_in_threadpool(
            _restore_under_lock, map_id, record, merge, actor
        )
    except MapLockBusy:
        raise HTTPException(
            status_code=429, detail=_BUSY_DETAIL.format(map_id=map_id)
        ) from None
    except RestoreError as exc:
        status = 404 if exc.code == "nothing_to_restore" else 400
        return add_no_cache(
            JSONResponse(
                {"ok": False, "code": exc.code, "detail": str(exc)},
                status_code=status,
            )
        )

    if outcome is None:
        return add_no_cache(
            JSONResponse(
                {
                    "ok": False,
                    "code": "live_data",
                    "detail": (
                        "This map already has chronicle data. Restoring would "
                        "mix two histories; wipe first, or resend with "
                        "merge: true to keep the live days and fill in the rest."
                    ),
                },
                status_code=409,
            )
        )
    result, restored_at = outcome

    return add_no_cache(
        JSONResponse(
            {
                "ok": True,
                "map": map_id,
                "backup_id": record.id,
                "merge": merge,
                "restored_days": result.restored_days,
                "restored_day_count": len(result.restored_days),
                "skipped_days": result.skipped_days,
                "restored_rows": result.restored_rows,
                "restored_at": restored_at,
                "restored_by": actor,
            }
        )
    )
