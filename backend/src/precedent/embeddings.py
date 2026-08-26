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


def embed(text: str, *, input_type: str = "document") -> list[float]:
    """Embed `text`. `input_type` is "document" when storing a case, "query" when searching."""
    return embed_batch([text], input_type=input_type)[0]


def embed_batch(texts: list[str], *, input_type: str = "document") -> list[list[float]]:
    """Embed multiple texts in one Voyage request (one call instead of len(texts))."""
    api_key = os.environ.get("VOYAGE_API_KEY", "").strip()
    if not api_key:
        raise EmbeddingError("VOYAGE_API_KEY is not set")
    try:
        resp = httpx.post(
            _VOYAGE_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={"input": texts, "model": _MODEL, "input_type": input_type},
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
