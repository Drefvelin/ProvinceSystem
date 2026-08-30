"""Shared CORS and cache headers for map file/JSON responses."""

from __future__ import annotations

import os
from email.utils import parsedate

from fastapi import Response
from fastapi.responses import FileResponse


def add_cors(response: Response) -> Response:
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response


def add_no_cache(response: Response) -> Response:
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def add_revalidate(response: Response) -> Response:
    """Let the browser keep the body but re-check it on every use.

    `no-cache` is not `no-store`: the browser stores the response and asks
    "still current?" before each use. A regenerated map is picked up as
    immediately as it was under `no-store`, but an unchanged one costs a 304
    with no body instead of re-sending the whole PNG.

    `private` keeps these authenticated responses out of shared proxy caches
    such as the public nginx in front of the API.
    """
    response.headers["Cache-Control"] = "private, no-cache, must-revalidate"
    return response


def _header_str(value: object) -> str | None:
    """Normalise a header argument to `str | None`.

    Routes declare these with `Header(default=None)`. FastAPI resolves that to a
    real value per request, but code that calls a route function directly (tests,
    one route delegating to another) receives the unresolved `Header` sentinel.
    Treat anything that is not a string as "client sent nothing".
    """
    return value if isinstance(value, str) else None


def _matches_etag(if_none_match: str, etag: str) -> bool:
    return etag in [tag.strip().removeprefix("W/") for tag in if_none_match.split(",")]


def _not_modified(if_modified_since: str, last_modified: str) -> bool:
    since = parsedate(if_modified_since)
    modified = parsedate(last_modified)
    return since is not None and modified is not None and since >= modified


def conditional_file_response(
    path: str | os.PathLike[str],
    *,
    media_type: str,
    if_none_match: str | None = None,
    if_modified_since: str | None = None,
) -> Response:
    """CORS-enabled `FileResponse` that answers 304 when the client is current.

    Stats the file up front so `etag`/`last-modified` exist before the body is
    sent, which is what makes the conditional check possible. `FileResponse`
    otherwise defers that stat until it streams.
    """
    if_none_match = _header_str(if_none_match)
    if_modified_since = _header_str(if_modified_since)

    stat_result = os.stat(path)
    response = FileResponse(path, media_type=media_type, stat_result=stat_result)
    add_revalidate(add_cors(response))

    etag = response.headers.get("etag", "")
    last_modified = response.headers.get("last-modified", "")

    if if_none_match:
        fresh = _matches_etag(if_none_match, etag)
    elif if_modified_since:
        fresh = _not_modified(if_modified_since, last_modified)
    else:
        fresh = False

    if not fresh:
        return response

    not_modified = Response(status_code=304)
    not_modified.headers["ETag"] = etag
    not_modified.headers["Last-Modified"] = last_modified
    return add_revalidate(add_cors(not_modified))
