"""Staff wipe of one realm's website character data (plugin-key route)."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("characters.realm_wipe")

# Order matters: character_wardrobe_slots and character_create_wardrobe carry no
# realm_id, so they are scoped through roster/creates and must go first.
WIPE_TABLES = (
    "character_wardrobe_slots",
    "character_create_wardrobe",
    "lore_item_customisations",
    "character_roster",
    "character_creates",
)

_SLOTS_IN_REALM = """
    EXISTS (
        SELECT 1 FROM character_roster cr
        WHERE cr.player_uuid = character_wardrobe_slots.player_uuid
          AND cr.character_id = character_wardrobe_slots.character_id
          AND cr.realm_id = ?
    )
    OR EXISTS (
        SELECT 1 FROM character_creates cc
        WHERE cc.player_uuid = character_wardrobe_slots.player_uuid
          AND cc.character_id = character_wardrobe_slots.character_id
          AND cc.realm_id = ?
    )
"""


def wipe_realm_character_data(realm_id: str | None = None) -> dict[str, Any]:
    """Delete this realm's character tables. Player rank/age meta is untouched."""
    from src.skins.codes import normalize_realm_id
    from src.skins.db import connect

    realm = normalize_realm_id(realm_id)
    deleted: dict[str, int] = {}
    relpaths: list[str] = []

    with connect() as conn:
        for row in conn.execute(
            f"SELECT png_relpath FROM character_wardrobe_slots WHERE {_SLOTS_IN_REALM}",
            (realm, realm),
        ).fetchall():
            if row["png_relpath"]:
                relpaths.append(str(row["png_relpath"]))
        for row in conn.execute(
            """
            SELECT png_relpath FROM character_create_wardrobe
            WHERE create_id IN (SELECT id FROM character_creates WHERE realm_id = ?)
            """,
            (realm,),
        ).fetchall():
            if row["png_relpath"]:
                relpaths.append(str(row["png_relpath"]))

        deleted["character_wardrobe_slots"] = conn.execute(
            f"DELETE FROM character_wardrobe_slots WHERE {_SLOTS_IN_REALM}",
            (realm, realm),
        ).rowcount
        deleted["character_create_wardrobe"] = conn.execute(
            """
            DELETE FROM character_create_wardrobe
            WHERE create_id IN (SELECT id FROM character_creates WHERE realm_id = ?)
            """,
            (realm,),
        ).rowcount
        deleted["lore_item_customisations"] = conn.execute(
            "DELETE FROM lore_item_customisations WHERE realm_id = ?",
            (realm,),
        ).rowcount
        deleted["character_roster"] = conn.execute(
            "DELETE FROM character_roster WHERE realm_id = ?",
            (realm,),
        ).rowcount
        deleted["character_creates"] = conn.execute(
            "DELETE FROM character_creates WHERE realm_id = ?",
            (realm,),
        ).rowcount
        conn.commit()

    pngs_deleted = _delete_pngs(relpaths)
    total = sum(max(count, 0) for count in deleted.values())
    logger.warning(
        "Wiped realm %s character data: %s row(s), %s png(s)",
        realm,
        total,
        pngs_deleted,
    )
    return {
        "realm_id": realm,
        "deleted": {table: max(deleted.get(table, 0), 0) for table in WIPE_TABLES},
        "total": total,
        "pngs_deleted": pngs_deleted,
    }


def _delete_pngs(relpaths: list[str]) -> int:
    from src.characters.wardrobe import delete_png_relpath

    done = 0
    for relpath in relpaths:
        try:
            if delete_png_relpath(relpath):
                done += 1
        except OSError as e:
            logger.warning("Realm wipe could not delete %s: %s", relpath, e)
    return done
