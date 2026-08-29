"""Supabase Postgres storage for precedent cases (pgvector similarity search)."""

from __future__ import annotations

import logging
import os
import re
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
#
# Public (imported by precedent_routes.py and returned to callers as
# `max_distance`) so consumers like the Discord bot can read the live cutoff
# instead of hardcoding a copy of it.
MAX_RELEVANT_DISTANCE = 0.60


def search_similar(
    embedding: list[float],
    limit: int = 3,
    players: list[str] | None = None,
    query_text: str = "",
) -> list[dict[str, Any]]:
    """Nearest-K search under the relevance cutoff, applying two soft boosts that
    only reorder rows already inside the cutoff (never exclude or bypass it):

    - `players`: rows whose `players` array overlaps (case-insensitively).
    - `query_text`: rows whose summary/rule/ruling/punishment lexically contain
      any word from the query (Postgres full-text search, OR'd word-by-word).
      This exists because embedding distance alone can rank a short,
      exact-wording case (e.g. a one-line "Xray" summary) below a longer,
      only-thematically-related one for a query like "player xraying" -- the
      literal word match rescues it into the top-`limit` slots it would
      otherwise lose on distance alone. Words are OR'd (any one word matching
      is enough), not AND'd, so a short summary matching only "xray" out of
      "player xraying" still gets boosted.

    An empty/typo'd `players` or `query_text` degrades to pure distance order.
    """
    conn = _connect()
    try:
        with conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            lowered = [p.strip().lower() for p in (players or []) if p.strip()]
            words = [w for w in re.findall(r"\w+", query_text or "") if len(w) > 2]
            cur.execute(
                """
                SELECT id, logged_by, players, summary, rule, ruling, punishment,
                       created_at, embedding <=> %s::vector AS distance
                FROM precedent_cases
                WHERE embedding <=> %s::vector < %s
                ORDER BY
                    (EXISTS (
                        SELECT 1 FROM unnest(players) AS p WHERE lower(p) = ANY(%s::text[])
                    )) DESC,
                    (EXISTS (
                        SELECT 1 FROM unnest(%s::text[]) AS w
                        WHERE to_tsvector(
                                  'english',
                                  summary || ' ' || rule || ' ' || ruling || ' ' || punishment
                              ) @@ plainto_tsquery('english', w)
                    )) DESC,
                    embedding <=> %s::vector
                LIMIT %s
                """,
                (
                    embedding,
                    embedding,
                    MAX_RELEVANT_DISTANCE,
                    lowered,
                    words,
                    embedding,
                    limit,
                ),
            )
            return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def delete_case(case_id: str) -> bool:
    """Delete a case by id. Returns True if a row was deleted, False if not found."""
    conn = _connect()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("DELETE FROM precedent_cases WHERE id = %s", (case_id,))
            return cur.rowcount > 0
    finally:
        conn.close()


def get_case(case_id: str) -> dict[str, Any] | None:
    conn = _connect()
    try:
        with conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, logged_by, players, summary, rule, ruling, punishment, created_at
                FROM precedent_cases WHERE id = %s
                """,
                (case_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def ping_db() -> None:
    """Cheap reachability check: connect and run SELECT 1. No embedding/Claude cost."""
    conn = _connect()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT 1")
    finally:
        conn.close()
