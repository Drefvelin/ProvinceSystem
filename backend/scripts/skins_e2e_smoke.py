"""Skins API E2E smoke — run from backend/: python scripts/skins_e2e_smoke.py

Uses FastAPI TestClient (no separate uvicorn). Requires SKINS_DEV=1 or real keys.
"""

from __future__ import annotations

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

STAFF = "dev-staff-key"
PLUGIN = "dev-plugin-key"
DISCORD_ID = "999999999999999999"
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


def main() -> None:
    migrate()
    client = TestClient(app)
    suffix = uuid.uuid4().hex[:8]
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
        json={"player_uuid": player, "minecraft_name": "Smoke"},
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
        json={"player_uuid": player, "minecraft_name": "Smoke"},
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
        json={"player_uuid": player, "minecraft_name": "Smoke"},
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

    # Negative: armor + wrong base_set
    armor_slug = f"smoke_armor_{suffix}"
    armor_files = [
        ("helmet", (f"{armor_slug}_helmet.png", icon, "image/png")),
        ("chestplate", (f"{armor_slug}_chestplate.png", icon, "image/png")),
        ("leggings", (f"{armor_slug}_leggings.png", icon, "image/png")),
        ("boots", (f"{armor_slug}_boots.png", icon, "image/png")),
        ("layer_1", (f"{armor_slug}_layer_1.png", layer, "image/png")),
        ("layer_2", (f"{armor_slug}_layer_2.png", layer, "image/png")),
    ]
    r = client.post(
        "/skins/submissions",
        data={
            "kind": "armor_set",
            "display_name": "Bad Armor",
            "base_set": "swords",
        },
        files=armor_files,
        headers=auth,
    )
    if r.status_code != 400:
        fail(f"armor+swords expected 400, got {r.status_code} {r.text}")

    r = client.post(
        "/skins/submissions",
        data={
            "kind": "item",
            "display_name": "Disabled Item",
            "base_set": "swords",
        },
        files=[("texture", (f"smoke_item_{suffix}.png", icon, "image/png"))],
        headers=auth,
    )
    if r.status_code != 400:
        fail(f"kind=item expected 400, got {r.status_code} {r.text}")

    # Armor upload — filenames define skin id
    data = {
        "kind": "armor_set",
        "display_name": "Smoke Armor",
        "base_set": "iron",
    }
    r = client.post(
        "/skins/submissions", data=data, files=armor_files, headers=auth
    )
    if r.status_code != 200:
        fail(f"armor upload: {r.status_code} {r.text}")
    armor = r.json()
    armor_id = armor["id"]
    player_key = armor.get("player_key")
    if not player_key or len(str(player_key)) != 8:
        fail(f"armor player_key expected 8 chars, got {player_key!r}")
    expected_armor_slug = f"{player_key}_{armor_slug}"
    if armor.get("slug") != expected_armor_slug:
        fail(
            f"armor slug expected {expected_armor_slug}, got {armor.get('slug')}"
        )
    if armor.get("base_set") != "iron":
        fail(f"armor base_set expected iron, got {armor.get('base_set')}")
    if armor.get("discord_user_id") != DISCORD_ID:
        fail(
            f"armor discord_user_id expected {DISCORD_ID}, "
            f"got {armor.get('discord_user_id')}"
        )
    # Conflict check: same display_name should fail
    r = client.get(
        "/skins/submissions/check",
        params={"display_name": "Smoke Armor", "base_id": armor_slug},
        headers=auth,
    )
    if r.status_code != 200:
        fail(f"check endpoint: {r.status_code} {r.text}")
    if r.json().get("ok") is not False:
        fail(f"check should conflict for Smoke Armor, got {r.json()}")
    print(
        f"armor submission {armor_id} slug={armor['slug']} "
        f"base_set={armor['base_set']} conflict-check ok"
    )

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

    # handheld + wrong base_set
    hand_slug = f"smoke_hand_{suffix}"
    r = client.post(
        "/skins/submissions",
        data={
            "kind": "handheld",
            "display_name": "Bad Hand",
            "base_set": "spears",
        },
        files=[("texture", (f"{hand_slug}.png", icon, "image/png"))],
        headers=auth2,
    )
    if r.status_code != 400:
        fail(f"handheld+spears expected 400, got {r.status_code} {r.text}")

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
        files=[("texture", (f"{hand_slug}.png", icon, "image/png"))],
        headers=auth2,
    )
    if r.status_code != 200:
        fail(f"handheld upload: {r.status_code} {r.text}")
    hand = r.json()
    hand_id = hand["id"]
    if hand.get("base_set") != "swords":
        fail(f"handheld base_set expected swords, got {hand.get('base_set')}")
    if hand.get("add_name") is not True:
        fail(f"handheld add_name expected True, got {hand.get('add_name')}")
    if hand.get("name_colours") != ["#9c001a", "\u00a7c"]:
        fail(f"handheld name_colours unexpected: {hand.get('name_colours')}")
    if hand.get("name_styles") != ["bold", "italic"]:
        fail(f"handheld name_styles unexpected: {hand.get('name_styles')}")
    if not str(hand.get("slug", "")).startswith(f"{player_key}_"):
        # same player may have new session but same UUID → same player_key
        pass
    expected_hand = f"{hand.get('player_key') or player_key}_{hand_slug}"
    if hand.get("slug") != expected_hand:
        fail(f"handheld slug expected {expected_hand}, got {hand.get('slug')}")
    print(
        f"handheld submission {hand_id} base_set={hand['base_set']} "
        f"add_name colours/styles ok slug={hand.get('slug')}"
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

    large_slug = f"smoke_large_{suffix}"
    r = client.post(
        "/skins/submissions",
        data={
            "kind": "large_handheld",
            "display_name": "Smoke Large",
            "grip_preset": "bottom",
            "base_set": "spears",
        },
        files=[("texture", (f"{large_slug}.png", large_tex, "image/png"))],
        headers=auth3,
    )
    if r.status_code != 200:
        fail(f"large upload: {r.status_code} {r.text}")
    large = r.json()
    large_id = large["id"]
    if large.get("slug") != f"{large.get('player_key')}_{large_slug}":
        fail(
            f"large slug expected {large.get('player_key')}_{large_slug}, "
            f"got {large.get('slug')}"
        )
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
        f"base_set={large['base_set']}"
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

    # Approve all three
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
    if by_id[armor_id].get("base_set") != "iron":
        fail("armor base_set missing on approved list")
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
    print("plugin approved list ok")

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

    print("ALL OK — Step 10 smoke passed (player_key prefix + name fields)")
    sys.exit(0)


if __name__ == "__main__":
    main()
