"""Precedent lookup API: staff log past cases, search for precedent on a new case."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from src.precedent.db import PrecedentDBError, insert_case, migrate, search_similar
from src.precedent.embeddings import EmbeddingError, embed
from src.precedent.synthesis import SynthesisError, synthesize
from src.skins.auth import HEADER_STAFF_KEY, require_staff_key

logger = logging.getLogger("precedent.routes")

precedent_router = APIRouter(prefix="/precedent", tags=["precedent"])


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
    logged_by: str = Field(..., min_length=1)
    players: list[str] = Field(default_factory=list)
    summary: str = Field(..., min_length=1)
    rule: str = Field(default="")
    ruling: str = Field(default="")
    punishment: str = Field(default="")


class SearchBody(BaseModel):
    query: str = Field(..., min_length=1)


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
    x_staff_key: str | None = Header(default=None, alias=HEADER_STAFF_KEY),
):
    _require_staff(x_staff_key)
    try:
        migrate()
        vector = embed(body.query, input_type="query")
        matches = search_similar(vector, limit=3)
        synthesis = synthesize(body.query, matches)
    except (PrecedentDBError, EmbeddingError, SynthesisError) as e:
        logger.exception("staff_search_precedent failed")
        raise HTTPException(status_code=502, detail=_client_detail(e)) from e
    return {"matches": [_serialize_match(m) for m in matches], "synthesis": synthesis}
