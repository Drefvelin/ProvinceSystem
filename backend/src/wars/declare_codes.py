"""One-time war declare codes: staff mint, the plugin validates then redeems.

Staff mint a code in Discord bound to an attacker faction, a defender faction and
a war goal. SimpleFactions validates it without consuming it, pins the declare GUI
to the code's goal, and only redeems once ``WarManager.declareWar`` returned a war.

No plaintext is stored, following ``discord_link_codes`` rather than ``codes``:
staff see the code once on mint, and a lost code is revoked and reminted.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from src.skins.codes import (
    generate_plaintext_code,
    hash_secret,
    normalize_realm_id,
)
from src.skins.db import connect


class WarDeclareCodeError(ValueError):
    """Invalid, expired, revoked, already-redeemed, or mismatched declare code."""


# Goals the in-game declare GUI actually offers. The other four WarGoalType values
# (OVERTHROW, CHANGE_LAW, CHANGE_TAX, FORCE_PEACE) are movement-origin only: they
# are raised by a political movement, never declared. Rejecting them at mint is a
# security boundary, not a convenience, so a code can never carry a goal the GUI
# would refuse to route.
DECLARABLE_GOALS = (
    "de_jure_annex",
    "subjugate",
    "transfer_subject",
    "war",
    "tributary",
    "usurp",
    "open_market",
    "change_government",
    "pillage",
)

MOVEMENT_ORIGIN_GOALS = ("overthrow", "change_law", "change_tax", "force_peace")

_FACTION_ID_MAX = 64
_LIST_LIMIT = 100


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_iso(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def _ttl_hours() -> int:
    raw = os.environ.get("WAR_CODE_TTL_HOURS", "48").strip()
    try:
        return max(1, int(raw))
    except ValueError:
        return 48


def _normalize_faction_id(value: str | None, label: str) -> str:
    raw = (value or "").strip()
    if not raw:
        raise WarDeclareCodeError(f"{label} is required")
    if len(raw) > _FACTION_ID_MAX:
        raise WarDeclareCodeError(f"{label} is too long")
    return raw


def _normalize_goal(value: str | None) -> str:
    raw = (value or "").strip().lower()
    if not raw:
        raise WarDeclareCodeError("goal is required")
    if raw in MOVEMENT_ORIGIN_GOALS:
        raise WarDeclareCodeError(
            f"'{raw}' is raised by a political movement, not declared, "
            "so it cannot be minted as a declare code"
        )
    if raw not in DECLARABLE_GOALS:
        allowed = ", ".join(DECLARABLE_GOALS)
        raise WarDeclareCodeError(f"goal must be one of: {allowed}")
    return raw


def _row_to_summary(row) -> dict:
    return {
        "id": int(row["id"]),
        "realm_id": str(row["realm_id"] or "main"),
        "attacker_faction_id": str(row["attacker_faction_id"]),
        "defender_faction_id": str(row["defender_faction_id"]),
        "goal": str(row["goal"]),
        "created_by_discord_id": row["created_by_discord_id"],
        "created_at": str(row["created_at"]),
        "expires_at": str(row["expires_at"]),
    }


def _load_usable(conn, code_hash: str, attacker: str, defender: str, realm: str):
    """Fetch a row and assert it is spendable by this exact pairing in this realm.

    Every rejection says "Invalid war code" for the not-found case so a caller
    cannot probe which codes exist, but says what is wrong once the code is known
    to be theirs, because the leader typing it needs to know why it failed.
    """
    row = conn.execute(
        "SELECT * FROM war_declare_codes WHERE code_hash = ?",
        (code_hash,),
    ).fetchone()
    if row is None:
        raise WarDeclareCodeError("Invalid war code")
    if str(row["realm_id"] or "main").strip().lower() != realm:
        raise WarDeclareCodeError("Invalid war code")
    if row["attacker_faction_id"] != attacker:
        raise WarDeclareCodeError("This code was not minted for your faction")
    if row["defender_faction_id"] != defender:
        raise WarDeclareCodeError("This code was not minted against that faction")
    if row["revoked"]:
        raise WarDeclareCodeError("This code has been revoked")
    if row["redeemed_at"]:
        raise WarDeclareCodeError("This code has already been used")
    if _parse_iso(str(row["expires_at"])) < _utcnow():
        raise WarDeclareCodeError("This code has expired")
    return row


def mint(
    attacker_faction_id: str,
    defender_faction_id: str,
    goal: str,
    realm_id: str | None = None,
    created_by_discord_id: str | None = None,
    ttl_hours: int | None = None,
) -> dict:
    """Create a code. The plaintext is returned once here and never stored."""
    attacker = _normalize_faction_id(attacker_faction_id, "attacker_faction_id")
    defender = _normalize_faction_id(defender_faction_id, "defender_faction_id")
    if attacker == defender:
        raise WarDeclareCodeError("A faction cannot declare war on itself")
    normalized_goal = _normalize_goal(goal)
    realm = normalize_realm_id(realm_id)

    hours = _ttl_hours() if ttl_hours is None else int(ttl_hours)
    if hours < 1:
        raise WarDeclareCodeError("ttl_hours must be at least 1")
    if hours > 24 * 30:
        raise WarDeclareCodeError("ttl_hours may not exceed 720 (30 days)")

    plaintext = generate_plaintext_code()
    now = _utcnow()
    expires_at = _iso(now + timedelta(hours=hours))
    creator = (created_by_discord_id or "").strip() or None

    with connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO war_declare_codes (
                code_hash, realm_id, attacker_faction_id, defender_faction_id,
                goal, created_by_discord_id, created_at, expires_at,
                redeemed_at, redeemed_war_id, revoked
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, 0)
            """,
            (
                hash_secret(plaintext),
                realm,
                attacker,
                defender,
                normalized_goal,
                creator,
                _iso(now),
                expires_at,
            ),
        )
        conn.commit()
        code_id = int(cur.lastrowid)

    return {
        "id": code_id,
        "code": plaintext,
        "realm_id": realm,
        "attacker_faction_id": attacker,
        "defender_faction_id": defender,
        "goal": normalized_goal,
        "expires_at": expires_at,
    }


def validate(
    code: str,
    attacker_faction_id: str,
    defender_faction_id: str,
    realm_id: str | None = None,
) -> dict:
    """Read-only check. Never consumes: the declare can still fail after this.

    ``WarGoalValidator``, ``CampaignDeclareValidator`` and ``CampaignNavyGate`` all
    run inside ``declareWar``, and a rejection there must not burn a staff-approved
    ticket, so redemption is a separate call.
    """
    plaintext = (code or "").strip()
    if not plaintext:
        raise WarDeclareCodeError("code is required")
    attacker = _normalize_faction_id(attacker_faction_id, "attacker_faction_id")
    defender = _normalize_faction_id(defender_faction_id, "defender_faction_id")
    realm = normalize_realm_id(realm_id)

    with connect() as conn:
        row = _load_usable(conn, hash_secret(plaintext), attacker, defender, realm)

    return {
        "valid": True,
        "id": int(row["id"]),
        "goal": str(row["goal"]),
        "realm_id": str(row["realm_id"] or "main"),
        "attacker_faction_id": str(row["attacker_faction_id"]),
        "defender_faction_id": str(row["defender_faction_id"]),
        "expires_at": str(row["expires_at"]),
    }


def redeem(
    code: str,
    attacker_faction_id: str,
    defender_faction_id: str,
    realm_id: str | None = None,
    war_id: str | None = None,
) -> dict:
    """Consume the code. Called only once the war exists."""
    plaintext = (code or "").strip()
    if not plaintext:
        raise WarDeclareCodeError("code is required")
    attacker = _normalize_faction_id(attacker_faction_id, "attacker_faction_id")
    defender = _normalize_faction_id(defender_faction_id, "defender_faction_id")
    realm = normalize_realm_id(realm_id)
    redeemed_at = _iso(_utcnow())

    with connect() as conn:
        row = _load_usable(conn, hash_secret(plaintext), attacker, defender, realm)
        # The WHERE guards against a second concurrent redeem of the same row.
        cur = conn.execute(
            """
            UPDATE war_declare_codes
            SET redeemed_at = ?, redeemed_war_id = ?
            WHERE id = ? AND redeemed_at IS NULL
            """,
            (redeemed_at, (war_id or "").strip() or None, int(row["id"])),
        )
        conn.commit()
        if cur.rowcount == 0:
            raise WarDeclareCodeError("This code has already been used")

    return {
        "ok": True,
        "id": int(row["id"]),
        "goal": str(row["goal"]),
        "realm_id": str(row["realm_id"] or "main"),
        "redeemed_at": redeemed_at,
        "war_id": (war_id or "").strip() or None,
    }


def list_outstanding(realm_id: str | None = None, limit: int | None = None) -> list[dict]:
    """Unredeemed, unrevoked, unexpired codes. Ids and metadata, never a code."""
    realm = normalize_realm_id(realm_id)
    capped = _LIST_LIMIT if limit is None else max(1, min(int(limit), _LIST_LIMIT))
    now = _iso(_utcnow())

    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM war_declare_codes
            WHERE realm_id = ?
              AND revoked = 0
              AND redeemed_at IS NULL
              AND expires_at > ?
            ORDER BY created_at ASC
            LIMIT ?
            """,
            (realm, now, capped),
        ).fetchall()

    return [_row_to_summary(row) for row in rows]


def revoke(code_id: int, realm_id: str | None = None) -> dict:
    """Kill a code by id. Staff never see plaintext again, so id is the handle."""
    realm = normalize_realm_id(realm_id)
    try:
        target = int(code_id)
    except (TypeError, ValueError) as e:
        raise WarDeclareCodeError("id must be a number") from e

    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM war_declare_codes WHERE id = ? AND realm_id = ?",
            (target, realm),
        ).fetchone()
        if row is None:
            raise WarDeclareCodeError("No such war code")
        if row["revoked"]:
            raise WarDeclareCodeError("This code has already been revoked")
        if row["redeemed_at"]:
            raise WarDeclareCodeError("This code has already been used")
        conn.execute(
            "UPDATE war_declare_codes SET revoked = 1 WHERE id = ?",
            (target,),
        )
        conn.commit()

    summary = _row_to_summary(row)
    summary["ok"] = True
    return summary
