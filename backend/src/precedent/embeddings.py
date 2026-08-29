"""Voyage AI text embeddings for precedent case storage/search."""

from __future__ import annotations

import logging
import os

import httpx

logger = logging.getLogger("precedent.embeddings")

_VOYAGE_URL = "https://api.voyageai.com/v1/embeddings"
_MODEL = "voyage-3"


class EmbeddingError(RuntimeError):
    """Raised when an embedding could not be produced."""


def embed(text: str, *, input_type: str | None = None) -> list[float]:
    """Embed `text`. See `embed_batch` for why `input_type` defaults to None."""
    return embed_batch([text], input_type=input_type)[0]


def embed_batch(texts: list[str], *, input_type: str | None = None) -> list[list[float]]:
    """Embed multiple texts in one Voyage request (one call instead of len(texts)).

    `input_type` is deliberately omitted by default. Voyage recommends
    "query"/"document" for asymmetric retrieval, where a short query is matched
    against long documents, but precedent search compares a short incident
    description against a short case summary. Measured on this corpus, the
    asymmetric prefixes added a near-constant 0.32-0.44 cosine penalty to every
    comparison regardless of how well the texts matched: byte-identical text
    scored 0.319-0.442 apart as query-vs-document, and 0.000 apart when embedded
    the same way. That offset consumed most of the usable distance range and
    made an exact match look mediocre.

    Embedding both sides identically also improved retrieval here: nearest-match
    distances fell for every test query, and the gap between relevant and
    off-topic queries widened from 0.061 to 0.097.

    Changing this invalidates every stored vector -- re-run
    `src/scripts/backfill_precedent_embeddings.py` over the whole corpus.
    """
    api_key = os.environ.get("VOYAGE_API_KEY", "").strip()
    if not api_key:
        raise EmbeddingError("VOYAGE_API_KEY is not set")
    payload: dict[str, object] = {"input": texts, "model": _MODEL}
    if input_type is not None:
        payload["input_type"] = input_type
    try:
        resp = httpx.post(
            _VOYAGE_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
            timeout=30.0,
        )
        resp.raise_for_status()
    except httpx.HTTPError as e:
        raise EmbeddingError(f"Voyage embedding request failed: {e}") from e
    data = resp.json()
    try:
        return [row["embedding"] for row in data["data"]]
    except (KeyError, TypeError) as e:
        raise EmbeddingError(f"Unexpected Voyage response shape: {e}") from e
