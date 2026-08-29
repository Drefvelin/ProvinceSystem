"""Precedent lookup API: staff log past cases, search for precedent on a new case."""

from __future__ import annotations

import logging
import time
from collections import defaultdict

import psycopg2
from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field, field_validator

from src.precedent.db import (
    MAX_RELEVANT_DISTANCE,
    PrecedentDBError,
    delete_case,
    get_case,
    insert_case,
    migrate,
    ping_db,
    search_similar,
)
from src.precedent.embeddings import EmbeddingError, embed
from src.precedent.synthesis import SynthesisError, synthesize
from src.skins.auth import HEADER_STAFF_KEY, require_staff_key

logger = logging.getLogger("precedent.routes")

precedent_router = APIRouter(prefix="/precedent", tags=["precedent"])

_SEARCH_RATE_BUCKETS: dict[str, list[float]] = defaultdict(list)
_SEARCH_RATE_LIMIT = 10
_SEARCH_RATE_WINDOW_SEC = 60.0


def _check_search_rate(client_ip: str) -> None:
    """Light rate limit: each search costs a Voyage embed + a Claude call."""
    now = time.monotonic()
    key = (client_ip or "").strip() or "unknown"
    bucket = _SEARCH_RATE_BUCKETS[key]
    cutoff = now - _SEARCH_RATE_WINDOW_SEC
    bucket[:] = [t for t in bucket if t > cutoff]
    if len(bucket) >= _SEARCH_RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many precedent search requests")
    bucket.append(now)


def _client_detail(e: Exception) -> str:
    """Generic, non-leaky detail for the caller. Full exception is logged server-side."""
    if isinstance(e, PrecedentDBError):
        return "Precedent database is unavailable. Check server logs."
    if isinstance(e, EmbeddingError):
        return "Embedding service is unavailable. Check server logs."
    if isinstance(e, SynthesisError):
        return "Synthesis service is unavailable. Check server logs."
    return "Precedent request failed. Check server logs."


def _require_staff(x_staff_key: str | None) -> None:
    try:
        require_staff_key(x_staff_key)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or missing staff key") from e


class LogCaseBody(BaseModel):
    logged_by: str = Field(..., min_length=1, max_length=200)
    players: list[str] = Field(default_factory=list, max_length=20)
    summary: str = Field(..., min_length=1, max_length=1000)
    rule: str = Field(default="", max_length=200)
    ruling: str = Field(default="", max_length=500)
    punishment: str = Field(default="", max_length=200)

    @field_validator("players")
    @classmethod
    def _cap_player_len(cls, v: list[str]) -> list[str]:
        for p in v:
            if len(p) > 200:
                raise ValueError("player name too long (max 200 chars)")
        return v


class SearchBody(BaseModel):
    query: str = Field(..., min_length=1)
    players: list[str] = Field(default_factory=list)


def _case_text(body: LogCaseBody) -> str:
    return (
        f"Summary: {body.summary}\n"
        f"Rule: {body.rule}\n"
        f"Ruling: {body.ruling}\n"
        f"Punishment: {body.punishment}"
    )


def _serialize_match(row: dict) -> dict:
    row = dict(row)
    row.pop("embedding", None)
    row["id"] = str(row["id"])
    if row.get("created_at") is not None:
        row["created_at"] = row["created_at"].isoformat()
    return row


@precedent_router.post("/staff/log")
def staff_log_case(
    body: LogCaseBody,
    x_staff_key: str | None = Header(default=None, alias=HEADER_STAFF_KEY),
):
    _require_staff(x_staff_key)
    try:
        migrate()
        vector = embed(_case_text(body), input_type="document")
        case_id = insert_case(
            logged_by=body.logged_by,
            players=body.players,
            summary=body.summary,
            rule=body.rule,
            ruling=body.ruling,
            punishment=body.punishment,
            embedding=vector,
        )
    except (PrecedentDBError, EmbeddingError) as e:
        logger.exception("staff_log_case failed")
        raise HTTPException(status_code=502, detail=_client_detail(e)) from e
    return {"id": case_id}


@precedent_router.post("/staff/search")
def staff_search_precedent(
    body: SearchBody,
    request: Request,
    x_staff_key: str | None = Header(default=None, alias=HEADER_STAFF_KEY),
):
    _require_staff(x_staff_key)
    _check_search_rate(request.client.host if request.client else "")
    try:
        migrate()
        vector = embed(body.query, input_type="query")
        matches = search_similar(vector, limit=3, players=body.players)
        synthesis = synthesize(body.query, matches)
    except (PrecedentDBError, EmbeddingError, SynthesisError) as e:
        logger.exception("staff_search_precedent failed")
        raise HTTPException(status_code=502, detail=_client_detail(e)) from e
    return {
        "matches": [_serialize_match(m) for m in matches],
        "synthesis": synthesis,
        "max_distance": MAX_RELEVANT_DISTANCE,
    }


@precedent_router.get("/staff/case/{case_id}")
def staff_get_case(
    case_id: str,
    x_staff_key: str | None = Header(default=None, alias=HEADER_STAFF_KEY),
):
    _require_staff(x_staff_key)
    try:
        migrate()
        case = get_case(case_id)
    except psycopg2.Error:
        raise HTTPException(status_code=400, detail="Invalid case id")
    except PrecedentDBError as e:
        logger.exception("staff_get_case failed")
        raise HTTPException(status_code=502, detail=_client_detail(e)) from e
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return _serialize_match(case)


@precedent_router.delete("/staff/case/{case_id}")
def staff_delete_case(
    case_id: str,
    x_staff_key: str | None = Header(default=None, alias=HEADER_STAFF_KEY),
):
    _require_staff(x_staff_key)
    try:
        migrate()
        deleted = delete_case(case_id)
    except psycopg2.Error:
        raise HTTPException(status_code=400, detail="Invalid case id")
    except PrecedentDBError as e:
        logger.exception("staff_delete_case failed")
        raise HTTPException(status_code=502, detail=_client_detail(e)) from e
    if not deleted:
        raise HTTPException(status_code=404, detail="Case not found")
    return {"deleted": True, "id": case_id}


@precedent_router.get("/staff/ping")
def staff_ping(
    x_staff_key: str | None = Header(default=None, alias=HEADER_STAFF_KEY),
):
    _require_staff(x_staff_key)
    try:
        ping_db()
    except PrecedentDBError as e:
        logger.exception("staff_ping failed")
        raise HTTPException(status_code=502, detail=_client_detail(e)) from e
    return {"ok": True}
