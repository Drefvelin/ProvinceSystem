"""Supabase Postgres storage for precedent cases (pgvector similarity search)."""

from __future__ import annotations

import logging
import os
from typing import Any

import psycopg2
import psycopg2.extras
from pgvector.psycopg2 import register_vector

logger = logging.getLogger("precedent.db")

_MIGRATED = False


class PrecedentDBError(RuntimeError):
    """Raised when the precedent database is not reachable or not configured."""


def _dsn() -> str:
    dsn = os.environ.get("SUPABASE_DB_URL", "").strip()
    if not dsn:
        raise PrecedentDBError("SUPABASE_DB_URL is not set")
    return dsn


def _connect():
    try:
        conn = psycopg2.connect(_dsn())
    except psycopg2.OperationalError as e:
        raise PrecedentDBError(f"Could not connect to precedent DB: {e}") from e
    register_vector(conn)
    return conn


def migrate() -> None:
    """Create the pgvector extension + precedent_cases table if missing. No-op once done."""
    global _MIGRATED
    if _MIGRATED:
        return
    if not os.environ.get("SUPABASE_DB_URL", "").strip():
        logger.warning("SUPABASE_DB_URL unset; precedent DB migration skipped")
        return
    conn = _connect()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS precedent_cases (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    logged_by TEXT NOT NULL,
                    players TEXT[] NOT NULL DEFAULT '{}',
                    summary TEXT NOT NULL,
                    rule TEXT NOT NULL DEFAULT '',
                    ruling TEXT NOT NULL DEFAULT '',
                    punishment TEXT NOT NULL DEFAULT '',
                    embedding VECTOR(1024) NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                """
            )
    finally:
        conn.close()
    _MIGRATED = True
    logger.info("Precedent DB migrated")


def insert_case(
    *,
    logged_by: str,
    players: list[str],
    summary: str,
    rule: str,
    ruling: str,
    punishment: str,
    embedding: list[float],
) -> str:
    conn = _connect()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO precedent_cases
                    (logged_by, players, summary, rule, ruling, punishment, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (logged_by, players, summary, rule, ruling, punishment, embedding),
            )
            row = cur.fetchone()
            return str(row[0])
    finally:
        conn.close()


# Empirical: cosine distance rarely exceeds ~0.65 even between unrelated real
# cases (general-purpose text embeddings compress everything into a narrow
# band), so a nearest-K search on an off-topic query still returns "matches"
# in the 0.6-0.65 range that overlap with genuinely weak-but-real matches.
# Cut those off entirely rather than force a top-3 slot on something that
# isn't actually relevant.
_MAX_RELEVANT_DISTANCE = 0.60


def search_similar(embedding: list[float], limit: int = 3) -> list[dict[str, Any]]:
    conn = _connect()
    try:
        with conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, logged_by, players, summary, rule, ruling, punishment,
                       created_at, embedding <=> %s::vector AS distance
                FROM precedent_cases
                WHERE embedding <=> %s::vector < %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (embedding, embedding, _MAX_RELEVANT_DISTANCE, embedding, limit),
            )
            return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()
