"""Map chronicle read routes + the localhost-gated manual capture trigger."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from .http_headers import add_no_cache, conditional_file_response, conditional_json_response
from .internal_access import require_localhost
from .map_access import ensure_map_access
from .map_registry import get_map_entry
from ..scripts.chronicle.store import (
    CHRONICLE_FILES,
    geometry_version,
    get_snapshot,
    is_valid_day,
    list_days,
    resolve_stored_file,
)
from ..scripts.util.dirs import defines_file

logger = logging.getLogger(__name__)

chronicle_router = APIRouter()

_GEOMETRY_FILENAME = "province_id_runs.bin.gz"

# How far back a manual snapshot may be aimed. The sources a capture reads
# (input/{map}/*.json, defines/{map}/*.json) only ever hold *current* state, so
# backfilling an old day stores today's data under a false date; the window
# exists purely so an operator can repair a gap the daily upload-triggered
# capture missed while the server was down. A month is comfortably longer than
# any realistic outage and short enough that the route cannot be used to spray
# thousands of day directories and index rows.
_MAX_BACKFILL_DAYS = 31
# map_name -> (mtime, size, sha256). The digest is a pure function of the
# artifact's bytes, so freshness-by-mtime+size is enough to reuse it and the
# index route stops re-hashing 353 KB on every request. Same idea as
# webp_cache._is_fresh; unbounded is fine because the key set is the map list.
_geometry_version_cache: dict[str, tuple[float, int, str | None]] = {}


def _cached_geometry_version(map_name: str) -> str | None:
    try:
        stat = os.stat(defines_file(map_name, _GEOMETRY_FILENAME))
    except OSError:
        # No artifact yet: let store decide what None means and cache nothing,
        # so the first build after this is picked up immediately.
        _geometry_version_cache.pop(map_name, None)
        return geometry_version(map_name)

    cached = _geometry_version_cache.get(map_name)
    if cached is not None and cached[0] == stat.st_mtime and cached[1] == stat.st_size:
        return cached[2]

    version = geometry_version(map_name)
    _geometry_version_cache[map_name] = (stat.st_mtime, stat.st_size, version)
    return version


def _run_capture(map_name: str, day: str | None, force: bool) -> None:
    """Background wrapper: capture_snapshot raises, a BackgroundTask must not.

    The 200 has already gone out by the time this runs, so a failure can only be
    reported in the log. capture_if_due swallows its own errors the same way;
    capture_snapshot deliberately keeps raising for direct callers.
    """
    from ..scripts.chronicle.capture import capture_snapshot

    try:
        capture_snapshot(map_name, day, force)
    except Exception:
        logger.warning(
            "Chronicle capture failed for map '%s' day '%s'",
            map_name,
            day,
            exc_info=True,
        )


def _is_capturable_day(day: str) -> bool:
    """A well-formed day inside the manual-capture window.

    is_valid_day alone accepts 0001-01-01 through 9999-12-31, which turns the
    trigger route into an unbounded directory + index-row generator.
    """
    if not is_valid_day(day):
        return False
    parsed = datetime.strptime(day, "%Y-%m-%d").date()
    today = datetime.now(timezone.utc).date()
    if parsed > today:
        # There is nothing to capture for a day that has not happened; a future
        # day would also sort ahead of every real snapshot in the index.
        return False
    return parsed >= today - timedelta(days=_MAX_BACKFILL_DAYS)


def _incomplete_days(map_id: str, days: list[str]) -> list[dict]:
    """Days whose manifest recorded a missing or unparsable source.

    The manifest is stored in the index row, so this is SQLite only - no
    filesystem access and no re-reading of day directories. One get_snapshot per
    day is a connect per day, which is fine at one row per day of history and
    keeps this route free of any new store API.
    """
    out: list[dict] = []
    for day in days:
        snapshot = get_snapshot(map_id, day)
        if snapshot is None:
            continue
        manifest = snapshot.get("manifest") or {}
        missing = [str(name) for name in (manifest.get("missing") or [])]
        invalid = [str(name) for name in (manifest.get("invalid") or [])]
        if missing or invalid:
            out.append({"day": day, "missing": missing, "invalid": invalid})
    return out


@chronicle_router.get("/{map_name}/chronicle/index")
async def get_chronicle_index(
    map_name: str,
    authorization: str | None = Header(default=None),
    if_none_match: str | None = Header(default=None),
):
    """Days available for scrubbing, plus the geometry the client should paint.

    A map that has never been captured is the normal state on day zero, so an
    empty index is a 200 with empty fields rather than a 404 — the viewer needs
    to be able to say "no history yet" without treating it as an error.

    Served through conditional_json_response like the other computed-JSON routes
    in data_routes: this is the one response that must never be heuristically
    cached, since a stale copy silently hides newly captured days. The ETag
    still turns an unchanged index into a bodiless 304.
    """
    entry = ensure_map_access(map_name, authorization)
    # Everything below keys off the *registry* id, never the raw path segment:
    # ensure_map_access normalises (strip + lower) before its lookup, so
    # "/%20MaIn/..." passes the gate as "main". Feeding the raw segment onward
    # either raised out of validate_map as a 500 or, worse, quietly queried a
    # map_id that does not exist and reported an empty history.
    map_id = entry.id

    days = list_days(map_id)
    incomplete = _incomplete_days(map_id, days)
    return conditional_json_response(
        {
            "days": days,
            "first": days[0] if days else None,
            "last": days[-1] if days else None,
            "geometry_version": _cached_geometry_version(map_id),
            # Additive only. A capture runs as a BackgroundTask after the 200
            # has gone out, so a source that was absent or torn is otherwise
            # visible only in the server log; surfacing it here lets a monitor
            # notice a permanently partial day without shelling into the box.
            "incomplete_days": incomplete,
            "incomplete_day_count": len(incomplete),
        },
        if_none_match=if_none_match,
    )


@chronicle_router.get("/{map_name}/chronicle/{day}/data/{name}")
async def get_chronicle_data(
    map_name: str,
    day: str,
    name: str,
    authorization: str | None = Header(default=None),
    if_none_match: str | None = Header(default=None),
    if_modified_since: str | None = Header(default=None),
):
    """One stored snapshot file, gzipped exactly as it sits on disk.

    `name` is checked against the fixed CHRONICLE_FILES tuple before any path is
    built, so a traversal attempt never reaches the filesystem at all. The body
    is served as application/gzip, which server.EXCLUDED_FROM_GZIP keeps the
    GZip middleware from re-compressing; the client gunzips it itself, the same
    way it already handles province_id_grid.bin.gz.
    """
    entry = ensure_map_access(map_name, authorization)
    map_id = entry.id  # see get_chronicle_index: never trust the raw segment

    if name not in CHRONICLE_FILES:
        raise HTTPException(status_code=400, detail=f"Unknown chronicle file '{name}'")
    if not is_valid_day(day):
        raise HTTPException(status_code=400, detail="Invalid chronicle day")

    path = resolve_stored_file(map_id, day, name)
    if path is None:
        return add_no_cache(JSONResponse({"error": "Snapshot not found"}, 404))

    try:
        return conditional_file_response(
            path,
            media_type="application/gzip",
            if_none_match=if_none_match,
            if_modified_since=if_modified_since,
        )
    except OSError:
        # resolve_stored_file checked existence; a wipe or a temp-file replace
        # between that check and the stat inside the response would otherwise
        # surface as an uncaught FileNotFoundError -> 500. The file is gone, so
        # the honest answer is the same 404 the missing-snapshot path gives.
        return add_no_cache(JSONResponse({"error": "Snapshot not found"}, 404))


@chronicle_router.post("/{map_name}/chronicle/snapshot")
async def create_chronicle_snapshot(
    map_name: str,
    request: Request,
    background_tasks: BackgroundTasks,
    day: str | None = None,
    force: bool = False,
):
    require_localhost(request)

    # require_localhost is not actually localhost-only (internal_access accepts
    # the RFC1918 ranges, i.e. the whole LAN on a game-server host), so it is
    # not a sufficient gate on its own: without a registry check any alphanumeric
    # string was an acceptable "map" and capture_snapshot would happily makedirs
    # a day directory, write a manifest and insert an index row for it.
    entry = get_map_entry(map_name)
    if entry is None:
        raise HTTPException(status_code=404, detail="Map not found")
    map_id = entry.id

    if day is not None and not _is_capturable_day(day):
        raise HTTPException(status_code=400, detail="Invalid chronicle day")

    background_tasks.add_task(_run_capture, map_id, day, force)

    return JSONResponse(
        content={
            "success": True,
            "map": map_id,
            "day": day,
            "force": force,
            "message": "Chronicle snapshot started.",
        }
    )
