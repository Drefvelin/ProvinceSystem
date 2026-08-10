"""Character create/list ingest smoke — run from backend/: python scripts/character_ingest_smoke.py
"""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

os.environ.setdefault("SKINS_DEV", "1")

from fastapi.testclient import TestClient

from server import app
from src.skins.db import connect, migrate

PLUGIN = "dev-plugin-key"
STAFF = "dev-staff-key"
IGN = "IngestSmoke"

ATTRS = [
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
]

# Spend exactly 12: three stats at +2 (3 each) = 9, three at +1 = 3 → 12
VALID_RANKS = {
    "strength": 2,
    "dexterity": 2,
    "constitution": 2,
    "intelligence": 1,
    "wisdom": 1,
    "charisma": 1,
}

CATALOG = {
    "stages": [
        {"id": "info", "type": "info", "order": 0, "messages": ["hi"]},
        {
            "id": "attributes_selection_stage",
            "type": "attributes",
            "order": 1,
            "points": 12,
            "max_rank": 2,
            "key": "attributes",
        },
    ],
    "attribute_point_buy": {
        "pool": 12,
        "max_rank": 2,
        "cost_for_rank": [1, 2],
        "attributes": ATTRS,
        "abbreviations": {
            "strength": "str",
            "dexterity": "dex",
            "constitution": "con",
            "intelligence": "int",
            "wisdom": "wis",
            "charisma": "cha",
        },
        "trait_id_pattern": "{abbr}{rank}",
    },
    "races": [{"id": "human", "name": "Human"}],
    "classes": [{"id": "warrior", "name": "Warrior"}],
    "traits": [
        {"id": "str1", "key": "attributes"},
        {"id": "str2", "key": "attributes"},
        {"id": "dex1", "key": "attributes"},
        {"id": "dex2", "key": "attributes"},
        {"id": "con1", "key": "attributes"},
        {"id": "con2", "key": "attributes"},
        {"id": "int1", "key": "attributes"},
        {"id": "int2", "key": "attributes"},
        {"id": "wis1", "key": "attributes"},
        {"id": "wis2", "key": "attributes"},
        {"id": "cha1", "key": "attributes"},
        {"id": "cha2", "key": "attributes"},
    ],
    "validation": {
        "name": {"min_length": 2, "max_length": 24},
        "age": {"minimum": 16},
        "description": {"min_length": 5, "max_length": 500},
        "clues": {
            "default_required": 1,
            "min_length": 3,
            "max_length": 100,
            "max_clues": 5,
        },
    },
    "slot_limits": {"hard_cap": 10, "defaults": {"max_alive_characters": 3}},
}


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def ensure_linked(client: TestClient, player: str, discord_id: str) -> None:
    r = client.post(
        "/skins/discord/link/start",
        json={"player_uuid": player, "minecraft_name": IGN},
        headers={"X-Plugin-Key": PLUGIN},
    )
    if r.status_code != 200:
        fail(f"link start: {r.status_code} {r.text}")
    body = r.json()
    if body.get("already_linked"):
        return
    r = client.post(
        "/skins/discord/link/complete",
        json={
            "code": body["code"],
            "discord_user_id": discord_id,
            "discord_username": "IngestSmokeDiscord",
        },
        headers={"X-Staff-Key": STAFF},
    )
    if r.status_code != 200:
        fail(f"link complete: {r.status_code} {r.text}")


def redeem_scope(client: TestClient, player: str, scope: str) -> str:
    r = client.post(
        "/skins/codes",
        json={"player_uuid": player, "scope": scope},
        headers={"X-Plugin-Key": PLUGIN},
    )
    if r.status_code != 200:
        fail(f"mint {scope}: {r.status_code} {r.text}")
    code = r.json()["code"]
    if scope == "character":
        r = client.post("/skins/character/redeem", json={"code": code})
    else:
        r = client.post("/skins/redeem", json={"code": code})
    if r.status_code != 200:
        fail(f"redeem {scope}: {r.status_code} {r.text}")
    return r.json()["session_token"]


def valid_body(**overrides):
    body = {
        "name": "Smoke Hero",
        "age": 20,
        "description": "A test character for ingest smoke.",
        "gender": "unspecified",
        "race_id": "human",
        "class_id": "warrior",
        "attributes": dict(VALID_RANKS),
        "traits": [],
        "clues": ["found a rusty key"],
    }
    body.update(overrides)
    return body


def main() -> None:
    migrate()
    client = TestClient(app)
    player = f"00000000-0000-4000-8000-{uuid.uuid4().hex[:12]}"
    discord_id = str(700000000000000000 + (uuid.uuid4().int % 99999999999999))

    r = client.put(
        "/characters/plugin/creation-catalog",
        json=CATALOG,
        headers={"X-Plugin-Key": PLUGIN},
    )
    if r.status_code != 200:
        fail(f"catalog put: {r.status_code} {r.text}")

    ensure_linked(client, player, discord_id)
    token = redeem_scope(client, player, "character")
    auth = {"Authorization": f"Bearer {token}"}

    bad = valid_body(attributes={a: 0 for a in ATTRS})
    r = client.post("/characters", json=bad, headers=auth)
    if r.status_code != 400:
        fail(f"bad attribute spend expected 400, got {r.status_code} {r.text}")
    print("OK invalid attribute spend -> 400")

    skin_token = redeem_scope(client, player, "skin")
    r = client.post(
        "/characters",
        json=valid_body(),
        headers={"Authorization": f"Bearer {skin_token}"},
    )
    if r.status_code != 401:
        fail(f"skin session create expected 401, got {r.status_code} {r.text}")
    print("OK skin session cannot POST /characters -> 401")

    req_id = str(uuid.uuid4())
    r = client.post(
        "/characters",
        json=valid_body(client_request_id=req_id),
        headers=auth,
    )
    if r.status_code != 200:
        fail(f"valid create: {r.status_code} {r.text}")
    create = r.json()
    create_id = create.get("id")
    if create.get("status") != "pending" or not create_id:
        fail(f"expected pending create: {create}")
    print(f"OK valid create -> pending id={create_id}")

    r = client.post(
        "/characters",
        json=valid_body(client_request_id=req_id, name="Other Name"),
        headers=auth,
    )
    if r.status_code != 200 or r.json().get("id") != create_id:
        fail(f"idempotent retry expected same id: {r.status_code} {r.text}")
    print("OK client_request_id idempotent")

    r = client.get("/characters/plugin/pending", headers={"X-Plugin-Key": PLUGIN})
    if r.status_code != 200:
        fail(f"plugin pending: {r.status_code} {r.text}")
    pending = r.json().get("creates") or []
    if not any(c.get("id") == create_id for c in pending):
        fail(f"create not in pending: {pending}")
    print("OK plugin pending contains create")

    r = client.post(
        "/characters/plugin/applied",
        json={
            "results": [
                {"id": create_id, "ok": True, "character_id": create_id},
            ]
        },
        headers={"X-Plugin-Key": PLUGIN},
    )
    if r.status_code != 200 or create_id not in (r.json().get("applied") or []):
        fail(f"applied ack: {r.status_code} {r.text}")
    print("OK plugin applied ack")

    r = client.put(
        "/characters/plugin/roster",
        json={
            "player_uuid": player,
            "characters": [
                {
                    "id": create_id,
                    "name": "Smoke Hero",
                    "status": "ALIVE",
                    "race": "human",
                    "class": "warrior",
                    "created_at": "100",
                }
            ],
        },
        headers={"X-Plugin-Key": PLUGIN},
    )
    if r.status_code != 200:
        fail(f"roster put: {r.status_code} {r.text}")

    r = client.get("/characters", headers=auth)
    if r.status_code != 200:
        fail(f"list: {r.status_code} {r.text}")
    listed = r.json()
    chars = listed.get("characters") or []
    if not any(c.get("id") == create_id and c.get("status") == "ALIVE" for c in chars):
        fail(f"list missing applied character: {chars}")
    # Without max_alive on roster, list falls back to catalog default (3)
    if listed.get("max_alive_characters") != 3:
        fail(
            f"list max_alive expected catalog default 3, got {listed.get('max_alive_characters')}"
        )
    print("OK list shows applied roster character")

    # Per-player entitlement from roster (LP max while online)
    r = client.put(
        "/characters/plugin/roster",
        json={
            "player_uuid": player,
            "max_alive_characters": 5,
            "characters": [
                {
                    "id": create_id,
                    "name": "Smoke Hero",
                    "status": "ALIVE",
                    "race": "human",
                    "class": "warrior",
                    "created_at": "100",
                }
            ],
        },
        headers={"X-Plugin-Key": PLUGIN},
    )
    if r.status_code != 200:
        fail(f"roster put with max: {r.status_code} {r.text}")

    r = client.get("/characters", headers=auth)
    if r.status_code != 200:
        fail(f"list after max: {r.status_code} {r.text}")
    listed = r.json()
    if listed.get("max_alive_characters") != 5:
        fail(f"list max_alive expected 5, got {listed.get('max_alive_characters')}")
    print("OK roster max_alive_characters=5 -> list returns 5")

    # Fill soft slot limit using player entitlement (5 alive)
    r = client.put(
        "/characters/plugin/roster",
        json={
            "player_uuid": player,
            "characters": [
                {
                    "id": f"slot-{i}",
                    "name": f"Slot {i}",
                    "status": "ALIVE",
                    "race": "human",
                    "class": "warrior",
                }
                for i in range(5)
            ],
        },
        headers={"X-Plugin-Key": PLUGIN},
    )
    if r.status_code != 200:
        fail(f"full roster put: {r.status_code} {r.text}")

    r = client.post("/characters", json=valid_body(), headers=auth)
    if r.status_code != 400 or "slot" not in r.text.lower():
        fail(f"over slot expected 400 slot, got {r.status_code} {r.text}")
    print("OK over soft slot limit (5) -> 400")

    # Offline-style roster omit must not clear stored entitlement
    r = client.put(
        "/characters/plugin/roster",
        json={
            "player_uuid": player,
            "characters": [
                {
                    "id": "slot-0",
                    "name": "Slot 0",
                    "status": "ALIVE",
                    "race": "human",
                    "class": "warrior",
                }
            ],
        },
        headers={"X-Plugin-Key": PLUGIN},
    )
    if r.status_code != 200:
        fail(f"roster omit max: {r.status_code} {r.text}")
    r = client.get("/characters", headers=auth)
    if r.status_code != 200 or r.json().get("max_alive_characters") != 5:
        fail(f"omit max should keep 5: {r.status_code} {r.text}")
    print("OK roster without max_alive keeps last entitlement")

    print("character_ingest_smoke: all checks passed")


if __name__ == "__main__":
    main()
