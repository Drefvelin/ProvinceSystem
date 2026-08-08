"""Skins API E2E smoke — run from backend/: python scripts/skins_e2e_smoke.py

Uses FastAPI TestClient (no separate uvicorn). Requires SKINS_DEV=1 or real keys.

Step 11: submission ids are `{sanitized_ign}_{slugify(display_name)}` (no
player_key, no filename-derived identity). Armor submissions carry 1–6 tiers
in one row; upload filenames are freeform and ignored by the server.
"""

from __future__ import annotations

import json
import os
import struct
import sys
import uuid
import zlib
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

os.environ.setdefault("SKINS_DEV", "1")

from fastapi.testclient import TestClient

from server import app
from src.skins.db import migrate
from src.skins.naming import ARMOR_FIELDS, build_submission_id

STAFF = "dev-staff-key"
PLUGIN = "dev-plugin-key"
DISCORD_ID = "999999999999999999"
IGN = "Smoke"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def make_png(w: int, h: int) -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    raw = b"".join(b"\x00" + bytes(w * 3) for _ in range(h))
    return (
        PNG_MAGIC
        + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def armor_tier_files(tiers: list[str], icon: bytes, layer: bytes) -> list[tuple]:
    """Multipart fields `{tier}_helmet` … `{tier}_layer_2`; filenames freeform."""
    files: list[tuple] = []
    for tier in tiers:
        for field in ARMOR_FIELDS[:4]:
            files.append((f"{tier}_{field}", ("art.png", icon, "image/png")))
        for field in ARMOR_FIELDS[4:]:
            files.append((f"{tier}_{field}", ("layer.png", layer, "image/png")))
    return files


def main() -> None:
    migrate()
    client = TestClient(app)
    player = "00000000-0000-0000-0000-000000000208"
    unlinked_player = f"00000000-0000-0000-0000-{uuid.uuid4().hex[:12]}"

    # Mint without Discord link must fail
    r = client.post(
        "/skins/codes",
        json={"player_uuid": unlinked_player},
        headers={"X-Plugin-Key": PLUGIN},
    )
    if r.status_code != 400:
        fail(f"issue code without link expected 400, got {r.status_code} {r.text}")
    if "linkdiscord" not in r.text.lower() and "discord" not in r.text.lower():
        fail(f"issue code without link expected discord message: {r.text}")

    # Discord link required before mint
    r = client.post(
        "/skins/discord/link/start",
        json={"player_uuid": player, "minecraft_name": IGN},
        headers={"X-Plugin-Key": PLUGIN},
    )
    if r.status_code != 200:
        fail(f"link start: {r.status_code} {r.text}")
    r = client.post(
        "/skins/discord/link/complete",
        json={
            "code": r.json()["code"],
            "discord_user_id": DISCORD_ID,
            "discord_username": "SmokeDiscord",
        },
        headers={"X-Staff-Key": STAFF},
    )
    if r.status_code != 200:
        fail(f"link complete: {r.status_code} {r.text}")

    # Already linked — no new code
    r = client.post(
        "/skins/discord/link/start",
        json={"player_uuid": player, "minecraft_name": IGN},
        headers={"X-Plugin-Key": PLUGIN},
    )
    if r.status_code != 200:
        fail(f"link start already: {r.status_code} {r.text}")
    already = r.json()
    if not already.get("already_linked"):
        fail(f"expected already_linked: {already}")
    if already.get("discord_username") != "SmokeDiscord":
        fail(f"expected discord_username SmokeDiscord: {already}")
    if "code" in already:
        fail(f"already linked should not return code: {already}")

    # Plugin notice from complete
    r = client.get("/skins/plugin/notices", headers={"X-Plugin-Key": PLUGIN})
    if r.status_code != 200:
        fail(f"plugin notices: {r.status_code} {r.text}")
    notices = r.json().get("notices") or []
    match = [
        n
        for n in notices
        if n.get("player_uuid") == player and n.get("type") == "link_success"
    ]
    if not match:
        fail(f"expected link_success notice for {player}: {notices}")
    notice_id = match[-1]["id"]
    if match[-1].get("payload", {}).get("discord_username") != "SmokeDiscord":
        fail(f"notice payload missing username: {match[-1]}")
    r = client.post(
        "/skins/plugin/notices/ack",
        json={"ids": [notice_id]},
        headers={"X-Plugin-Key": PLUGIN},
    )
    if r.status_code != 200:
        fail(f"ack notices: {r.status_code} {r.text}")
    if notice_id not in (r.json().get("acked") or []):
        fail(f"ack missing notice id: {r.text}")
    r = client.get("/skins/plugin/notices", headers={"X-Plugin-Key": PLUGIN})
    if any(n.get("id") == notice_id for n in (r.json().get("notices") or [])):
        fail("acked notice still undelivered")

    # Issue + active list + redeem
    r = client.post(
        "/skins/codes",
        json={"player_uuid": player},
        headers={"X-Plugin-Key": PLUGIN},
    )
    if r.status_code != 200:
        fail(f"issue code: {r.status_code} {r.text}")
    code = r.json()["code"]

    r = client.get("/skins/plugin/codes/active", headers={"X-Plugin-Key": PLUGIN})
    if r.status_code != 200:
        fail(f"list active codes: {r.status_code} {r.text}")
    active_codes = [c.get("code") for c in r.json().get("codes", [])]
    if code not in active_codes:
        fail(f"issued code missing from active list: {active_codes}")

    # Separate code for revoke path
    r = client.post(
        "/skins/codes",
        json={"player_uuid": player},
        headers={"X-Plugin-Key": PLUGIN},
    )
    if r.status_code != 200:
        fail(f"issue revoke-target code: {r.status_code} {r.text}")
    revoke_target = r.json()["code"]
    r = client.post(
        "/skins/plugin/codes/revoke",
        json={"code": revoke_target},
        headers={"X-Plugin-Key": PLUGIN},
    )
    if r.status_code != 200 or not r.json().get("ok"):
        fail(f"revoke code: {r.status_code} {r.text}")
    r = client.get("/skins/plugin/codes/active", headers={"X-Plugin-Key": PLUGIN})
    if revoke_target in [c.get("code") for c in r.json().get("codes", [])]:
        fail("revoked code still in active list")
    r = client.post("/skins/redeem", json={"code": revoke_target})
    if r.status_code != 400:
        fail(f"redeem revoked expected 400, got {r.status_code} {r.text}")

    r = client.post("/skins/redeem", json={"code": code})
    if r.status_code != 200:
        fail(f"redeem: {r.status_code} {r.text}")
    token = r.json()["session_token"]
    auth = {"Authorization": f"Bearer {token}"}

    # Unlink by UUID then re-link (guards + unlink path)
    r = client.post(
        "/skins/discord/link/unlink",
        json={"player_uuid": player},
        headers={"X-Plugin-Key": PLUGIN},
    )
    if r.status_code != 200 or not r.json().get("ok"):
        fail(f"unlink by uuid: {r.status_code} {r.text}")
    r = client.post(
        "/skins/discord/link/unlink",
        json={"player_uuid": player},
        headers={"X-Plugin-Key": PLUGIN},
    )
    if r.status_code != 400:
        fail(f"unlink when not linked expected 400, got {r.status_code} {r.text}")

    r = client.post(
        "/skins/discord/link/start",
        json={"player_uuid": player, "minecraft_name": IGN},
        headers={"X-Plugin-Key": PLUGIN},
    )
    if r.status_code != 200:
        fail(f"link start 2: {r.status_code} {r.text}")
    r = client.post(
        "/skins/discord/link/complete",
        json={
            "code": r.json()["code"],
            "discord_user_id": DISCORD_ID,
            "discord_username": "SmokeDiscord",
        },
        headers={"X-Staff-Key": STAFF},
    )
    if r.status_code != 200:
        fail(f"link complete 2: {r.status_code} {r.text}")

    # One-time skins code: second redeem must fail
    r = client.post("/skins/redeem", json={"code": code})
    if r.status_code != 400:
        fail(f"second redeem expected 400, got {r.status_code} {r.text}")

    icon = make_png(16, 16)
    layer = make_png(64, 32)
    large_tex = make_png(32, 32)

    # kind=item is disabled regardless of Step 11 changes
    r = client.post(
        "/skins/submissions",
        data={
            "kind": "item",
            "display_name": "Disabled Item",
            "base_set": "swords",
        },
        files=[("texture", ("art.png", icon, "image/png"))],
        headers=auth,
    )
    if r.status_code != 400:
        fail(f"kind=item expected 400, got {r.status_code} {r.text}")

    # Negative: armor with no tiers and no legacy unprefixed fields
    r = client.post(
        "/skins/submissions",
        data={"kind": "armor_set", "display_name": "Bad Armor No Tiers"},
        headers=auth,
    )
    if r.status_code != 400:
        fail(f"armor no tiers expected 400, got {r.status_code} {r.text}")

    # Negative: armor with an invalid tier name
    r = client.post(
        "/skins/submissions",
        data={
            "kind": "armor_set",
            "display_name": "Bad Armor Tier",
            "tiers": json.dumps(["swords"]),
        },
        headers=auth,
    )
    if r.status_code != 400:
        fail(f"armor invalid tier expected 400, got {r.status_code} {r.text}")

    # Negative: armor with a duplicate tier
    r = client.post(
        "/skins/submissions",
        data={
            "kind": "armor_set",
            "display_name": "Bad Armor Dup Tier",
            "tiers": json.dumps(["iron", "iron"]),
        },
        headers=auth,
    )
    if r.status_code != 400:
        fail(f"armor duplicate tier expected 400, got {r.status_code} {r.text}")

    # Multi-tier armor upload — ids come from IGN + item name, filenames are freeform
    armor_tiers = ["iron", "steel"]
    r = client.post(
        "/skins/submissions",
        data={
            "kind": "armor_set",
            "display_name": "Smoke Armor",
            "tiers": json.dumps(armor_tiers),
        },
        files=armor_tier_files(armor_tiers, icon, layer),
        headers=auth,
    )
    if r.status_code != 200:
        fail(f"armor upload: {r.status_code} {r.text}")
    armor = r.json()
    armor_id = armor["id"]
    expected_armor_id = build_submission_id(IGN, "Smoke Armor")
    if armor_id != expected_armor_id:
        fail(f"armor id expected {expected_armor_id}, got {armor_id}")
    if armor.get("slug") != armor_id:
        fail(f"armor slug expected to equal id, got {armor.get('slug')}")
    if armor.get("tiers") != armor_tiers:
        fail(f"armor tiers expected {armor_tiers}, got {armor.get('tiers')}")
    if armor.get("base_set") is not None:
        fail(f"armor base_set expected null, got {armor.get('base_set')}")
    if armor.get("discord_user_id") != DISCORD_ID:
        fail(
            f"armor discord_user_id expected {DISCORD_ID}, "
            f"got {armor.get('discord_user_id')}"
        )
    print(
        f"armor submission {armor_id} tiers={armor['tiers']} "
        f"base_set={armor.get('base_set')!r} ok"
    )

    # Conflict check: display_name only (no base_id) — active armor blocks a re-submit
    r = client.get(
        "/skins/submissions/check",
        params={"display_name": "Smoke Armor"},
        headers=auth,
    )
    if r.status_code != 200:
        fail(f"check endpoint: {r.status_code} {r.text}")
    if r.json().get("ok") is not False:
        fail(f"check should conflict for Smoke Armor, got {r.json()}")
    print("armor conflict-check (display_name only) ok")

    # Backward-compat: legacy unprefixed armor fields + base_set select a single tier
    legacy_files = [
        (field, ("art.png", icon if field in ARMOR_FIELDS[:4] else layer, "image/png"))
        for field in ARMOR_FIELDS
    ]
    r = client.post(
        "/skins/submissions",
        data={
            "kind": "armor_set",
            "display_name": "Smoke Armor Legacy",
            "base_set": "iron",
        },
        files=legacy_files,
        headers=auth,
    )
    if r.status_code != 200:
        fail(f"legacy armor upload: {r.status_code} {r.text}")
    legacy_armor = r.json()
    legacy_armor_id = legacy_armor["id"]
    if legacy_armor.get("tiers") != ["iron"]:
        fail(f"legacy armor tiers expected ['iron'], got {legacy_armor.get('tiers')}")
    if legacy_armor.get("base_set") is not None:
        fail(f"legacy armor base_set expected null, got {legacy_armor.get('base_set')}")
    print(f"legacy single-tier armor {legacy_armor_id} tiers={legacy_armor['tiers']} ok")

    staff = {"X-Staff-Key": STAFF}
    r = client.get("/skins/staff/notifications", headers=staff)
    if r.status_code != 200:
        fail(f"notifications: {r.status_code} {r.text}")
    notes = [
        n
        for n in r.json().get("notifications", [])
        if n.get("submission_id") == armor_id and n.get("type") == "submitted"
    ]
    if not notes:
        fail(f"no submitted notification for armor {armor_id}")
    nid = notes[0]["id"]
    if notes[0].get("discord_user_id") != DISCORD_ID:
        fail("submitted notification discord_user_id mismatch")
    r = client.post(f"/skins/staff/notifications/{nid}/ack", headers=staff)
    if r.status_code != 200:
        fail(f"notification ack: {r.status_code} {r.text}")
    r = client.get("/skins/staff/notifications", headers=staff)
    if any(n.get("id") == nid for n in r.json().get("notifications", [])):
        fail("notification still listed after ack")
    print(f"submitted notification {nid} ok")

    # New session for second submission (code already redeemed — issue another)
    r = client.post(
        "/skins/codes",
        json={"player_uuid": player},
        headers={"X-Plugin-Key": PLUGIN},
    )
    if r.status_code != 200:
        fail(f"issue code 2: {r.status_code} {r.text}")
    r = client.post("/skins/redeem", json={"code": r.json()["code"]})
    if r.status_code != 200:
        fail(f"redeem 2: {r.status_code} {r.text}")
    auth2 = {"Authorization": f"Bearer {r.json()['session_token']}"}

    # handheld + wrong base_set (still validated for non-armor kinds)
    r = client.post(
        "/skins/submissions",
        data={
            "kind": "handheld",
            "display_name": "Bad Hand",
            "base_set": "spears",
        },
        files=[("texture", ("whatever.png", icon, "image/png"))],
        headers=auth2,
    )
    if r.status_code != 400:
        fail(f"handheld+spears expected 400, got {r.status_code} {r.text}")

    # handheld upload — id from IGN + item name, freeform filename OK
    r = client.post(
        "/skins/submissions",
        data={
            "kind": "handheld",
            "display_name": "Smoke Hand",
            "base_set": "swords",
            "add_name": "true",
            "name_colours": '["#9c001a", "&c"]',
            "name_styles": '["bold", "italic"]',
        },
        files=[("texture", ("my_cool_texture_v2.png", icon, "image/png"))],
        headers=auth2,
    )
    if r.status_code != 200:
        fail(f"handheld upload: {r.status_code} {r.text}")
    hand = r.json()
    hand_id = hand["id"]
    expected_hand_id = build_submission_id(IGN, "Smoke Hand")
    if hand_id != expected_hand_id:
        fail(f"hand id expected {expected_hand_id}, got {hand_id}")
    if hand.get("slug") != hand_id:
        fail(f"hand slug expected to equal id, got {hand.get('slug')}")
    if hand.get("base_set") != "swords":
        fail(f"handheld base_set expected swords, got {hand.get('base_set')}")
    if hand.get("add_name") is not True:
        fail(f"handheld add_name expected True, got {hand.get('add_name')}")
    if hand.get("name_colours") != ["#9c001a", "\u00a7c"]:
        fail(f"handheld name_colours unexpected: {hand.get('name_colours')}")
    if hand.get("name_styles") != ["bold", "italic"]:
        fail(f"handheld name_styles unexpected: {hand.get('name_styles')}")
    print(
        f"handheld submission {hand_id} base_set={hand['base_set']} "
        f"add_name colours/styles ok (freeform filename)"
    )

    # Third session for large
    r = client.post(
        "/skins/codes",
        json={"player_uuid": player},
        headers={"X-Plugin-Key": PLUGIN},
    )
    if r.status_code != 200:
        fail(f"issue code 3: {r.status_code} {r.text}")
    r = client.post("/skins/redeem", json={"code": r.json()["code"]})
    if r.status_code != 200:
        fail(f"redeem 3: {r.status_code} {r.text}")
    auth3 = {"Authorization": f"Bearer {r.json()['session_token']}"}

    r = client.post(
        "/skins/submissions",
        data={
            "kind": "large_handheld",
            "display_name": "Smoke Large",
            "grip_preset": "bottom",
            "base_set": "spears",
        },
        files=[("texture", ("large-texture-final.png", large_tex, "image/png"))],
        headers=auth3,
    )
    if r.status_code != 200:
        fail(f"large upload: {r.status_code} {r.text}")
    large = r.json()
    large_id = large["id"]
    expected_large_id = build_submission_id(IGN, "Smoke Large")
    if large_id != expected_large_id:
        fail(f"large id expected {expected_large_id}, got {large_id}")
    if large.get("slug") != large_id:
        fail(f"large slug expected to equal id, got {large.get('slug')}")
    if large.get("grip_preset") != "bottom":
        fail(f"expected grip_preset=bottom, got {large.get('grip_preset')}")
    if large.get("base_set") != "spears":
        fail(f"large base_set expected spears, got {large.get('base_set')}")
    if large.get("discord_user_id") != DISCORD_ID:
        fail(
            f"large discord_user_id expected {DISCORD_ID}, "
            f"got {large.get('discord_user_id')}"
        )
    print(
        f"large submission {large_id} grip={large['grip_preset']} "
        f"base_set={large['base_set']} (freeform filename)"
    )

    for sid, label in (
        (armor_id, "armor"),
        (hand_id, "handheld"),
        (large_id, "large"),
    ):
        r = client.get(f"/skins/submissions/{sid}/review-sheet", headers=staff)
        if r.status_code != 200:
            fail(f"review-sheet {label}: {r.status_code} {r.text}")
        if not r.content.startswith(PNG_MAGIC):
            fail(f"review-sheet {label}: not a PNG")
        print(f"review-sheet {label} ok ({len(r.content)} bytes)")

    r = client.get(f"/skins/submissions/{armor_id}/review-sheet")
    if r.status_code != 401:
        fail(f"review-sheet without key expected 401, got {r.status_code}")

    # Approve all three (leave legacy_armor pending)
    for sid in (armor_id, hand_id, large_id):
        r = client.post(f"/skins/submissions/{sid}/approve", headers=staff)
        if r.status_code != 200:
            fail(f"approve {sid}: {r.status_code} {r.text}")

    plugin = {"X-Plugin-Key": PLUGIN}
    r = client.get("/skins/plugin/approved", headers=plugin)
    if r.status_code != 200:
        fail(f"plugin approved: {r.status_code} {r.text}")
    by_id = {s["id"]: s for s in r.json().get("submissions", [])}
    if armor_id not in by_id:
        fail("armor missing from plugin approved list")
    if hand_id not in by_id:
        fail("handheld missing from plugin approved list")
    if large_id not in by_id:
        fail("large missing from plugin approved list")
    if sorted(by_id[armor_id].get("tiers") or []) != sorted(armor_tiers):
        fail(
            f"armor tiers missing/incomplete on approved list: "
            f"{by_id[armor_id].get('tiers')}"
        )
    if "iron" not in by_id[armor_id].get("tiers", []):
        fail("armor approved tiers missing iron")
    if "steel" not in by_id[armor_id].get("tiers", []):
        fail("armor approved tiers missing steel")
    if by_id[armor_id].get("base_set") is not None:
        fail("armor base_set expected null on approved list")
    if by_id[hand_id].get("base_set") != "swords":
        fail("handheld base_set missing on approved list")
    if by_id[large_id].get("grip_preset") != "bottom":
        fail("large grip_preset missing on approved list")
    if by_id[large_id].get("base_set") != "spears":
        fail("large base_set missing on approved list")
    if by_id[hand_id].get("add_name") is not True:
        fail("handheld add_name missing on approved list")
    if by_id[hand_id].get("name_colours") != ["#9c001a", "\u00a7c"]:
        fail(
            "handheld name_colours missing on approved list: "
            f"{by_id[hand_id].get('name_colours')}"
        )
    if by_id[hand_id].get("name_styles") != ["bold", "italic"]:
        fail(
            "handheld name_styles missing on approved list: "
            f"{by_id[hand_id].get('name_styles')}"
        )
    print("plugin approved list ok (armor tiers include iron+steel, base_set null)")

    r = client.post(
        "/skins/plugin/applied",
        json={"submission_ids": [armor_id]},
        headers=plugin,
    )
    if r.status_code != 200:
        fail(f"applied: {r.status_code} {r.text}")
    if armor_id not in r.json().get("applied", []):
        fail("armor not in applied response")

    r = client.get("/skins/plugin/approved", headers=plugin)
    by_id = {s["id"]: s for s in r.json().get("submissions", [])}
    if armor_id in by_id:
        fail("armor still on approved list after applied")
    if large_id not in by_id:
        fail("large should still be on approved list")
    print("applied ack ok")

    # Deletable/tab-complete list uses human ids, not UUIDs
    r = client.get("/skins/plugin/submissions/deletable", headers=plugin)
    if r.status_code != 200:
        fail(f"deletable list: {r.status_code} {r.text}")
    deletable_ids = {s.get("id") for s in r.json().get("submissions", [])}
    for sid in (hand_id, large_id, legacy_armor_id):
        if sid not in deletable_ids:
            fail(f"deletable list missing {sid}: {deletable_ids}")
    for sid in deletable_ids:
        if not isinstance(sid, str) or "-" in sid:
            fail(f"deletable id looks like a UUID, expected human id: {sid}")
    print("deletable list ok (human ids, tab-complete ready)")

    print("ALL OK — Step 11 smoke (IGN ids + multi-tier)")
    sys.exit(0)


if __name__ == "__main__":
    main()
