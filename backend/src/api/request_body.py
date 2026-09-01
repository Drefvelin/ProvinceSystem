"""Shared bounded JSON body reader.

Lives here rather than in `data_routes` so the staff routes can reuse it
without importing a router module (and without either module importing the
other). `data_routes._read_json_body` is kept as an alias.
"""

from __future__ import annotations

import json

from fastapi import HTTPException, Request


async def read_json_body(request: Request, limit: int):
    """`request.json()` with a hard byte ceiling, streamed rather than buffered.

    Starlette's own `request.json()` reads the whole body into memory with no
    bound, so a single POST could pin an arbitrary amount of RAM. The parsed
    result is identical for anything under `limit`; only the failure modes are
    new — 413 for an oversize body, 400 for one that is not JSON (previously an
    uncaught JSONDecodeError, i.e. a 500).

    `RecursionError` is caught alongside `ValueError`: `json.loads` raises it,
    not a JSONDecodeError, on a deeply nested body (8 MiB of `[[[[…]]]]`), and
    an uncaught one is a 500 for what is plainly a malformed request.
    """
    declared = request.headers.get("content-length")
    if declared is not None:
        try:
            if int(declared) > limit:
                raise HTTPException(status_code=413, detail="Upload body too large")
        except ValueError:
            # A malformed Content-Length is not authoritative either way; fall
            # through and let the streamed count below decide.
            pass

    # A bytearray, not a list of chunks plus `b"".join`: the join holds the
    # chunk list and the joined copy at the same time, so peak memory was twice
    # the body. Appending amortises the same way the list did.
    body = bytearray()
    async for chunk in request.stream():
        if len(body) + len(chunk) > limit:
            # Stop reading rather than draining the rest: the body is already
            # past the ceiling and nothing downstream will use it.
            raise HTTPException(status_code=413, detail="Upload body too large")
        body += chunk

    try:
        return json.loads(body)
    except (ValueError, RecursionError) as exc:
        raise HTTPException(status_code=400, detail="Malformed JSON body") from exc
