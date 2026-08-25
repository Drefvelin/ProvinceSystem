"""Seed local mock code TEST-CODE-1. Run from backend/: python src/skins/seed_dev_code.py"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Allow `python src/skins/seed_dev_code.py` from backend/
_BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from src.skins.codes import hash_secret
from src.skins.db import connect, migrate

DEV_CODE = "TEST-CODE-1"
DEV_UUID = "00000000-0000-0000-0000-000000000001"


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> None:
    migrate()
    now = datetime.now(timezone.utc)
    expires_at = _iso(now + timedelta(hours=48))
    created_at = _iso(now)
    code_hash = hash_secret(DEV_CODE)

    with connect() as conn:
        existing = conn.execute(
            "SELECT id FROM codes WHERE code_hash = ?",
            (code_hash,),
        ).fetchone()

        if existing:
            conn.execute(
                """
                UPDATE codes
                SET player_uuid = ?, scope = 'skin', code_plaintext = ?,
                    created_at = ?, expires_at = ?,
                    redeemed_at = NULL, revoked = 0
                WHERE id = ?
                """,
                (DEV_UUID, DEV_CODE, created_at, expires_at, existing["id"]),
            )
            action = "updated"
        else:
            conn.execute(
                """
                INSERT INTO codes (
                    code_hash, code_plaintext, player_uuid, scope,
                    created_at, expires_at, redeemed_at, revoked
                )
                VALUES (?, ?, ?, 'skin', ?, ?, NULL, 0)
                """,
                (code_hash, DEV_CODE, DEV_UUID, created_at, expires_at),
            )
            action = "inserted"
        conn.commit()

    print(f"Seed {action}: code={DEV_CODE} uuid={DEV_UUID} expires_at={expires_at}")
    print("Set SKINS_DEV=1 (see backend/.env.example) for local plugin/staff keys.")


if __name__ == "__main__":
    main()
