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

    # Issue + redeem
    r = client.post(
        "/skins/codes",
        json={"player_uuid": player},
        headers={"X-Plugin-Key": PLUGIN},
    )
    if r.status_code != 200:
        fail(f"issue code: {r.status_code} {r.text}")
    code = r.json()["code"]

    r = client.post("/skins/redeem", json={"code": code})
    if r.status_code != 200:
        fail(f"redeem: {r.status_code} {r.text}")
    token = r.json()["session_token"]
    auth = {"Authorization": f"Bearer {token}"}

    icon = make_png(16, 16)
    layer = make_png(64, 32)
    large_tex = make_png(32, 32)

    # Armor upload
    armor_slug = f"smoke_armor_{suffix}"
    files = [
        ("helmet", ("h.png", icon, "image/png")),
        ("chestplate", ("c.png", icon, "image/png")),
        ("leggings", ("l.png", icon, "image/png")),
        ("boots", ("b.png", icon, "image/png")),
        ("layer_1", ("l1.png", layer, "image/png")),
        ("layer_2", ("l2.png", layer, "image/png")),
    ]
    data = {
        "kind": "armor_set",
        "slug": armor_slug,
        "display_name": "Smoke Armor",
    }
    r = client.post("/skins/submissions", data=data, files=files, headers=auth)
    if r.status_code != 200:
        fail(f"armor upload: {r.status_code} {r.text}")
    armor_id = r.json()["id"]
    print(f"armor submission {armor_id}")

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

    large_slug = f"smoke_large_{suffix}"
    r = client.post(
        "/skins/submissions",
        data={
            "kind": "large_handheld",
            "slug": large_slug,
            "display_name": "Smoke Large",
            "grip_preset": "bottom",
        },
        files=[("texture", ("t.png", large_tex, "image/png"))],
        headers=auth2,
    )
    if r.status_code != 200:
        fail(f"large upload: {r.status_code} {r.text}")
    large = r.json()
    large_id = large["id"]
    if large.get("grip_preset") != "bottom":
        fail(f"expected grip_preset=bottom, got {large.get('grip_preset')}")
    print(f"large submission {large_id} grip={large['grip_preset']}")

    staff = {"X-Staff-Key": STAFF}
    for sid, label in ((armor_id, "armor"), (large_id, "large")):
        r = client.get(f"/skins/submissions/{sid}/review-sheet", headers=staff)
        if r.status_code != 200:
            fail(f"review-sheet {label}: {r.status_code} {r.text}")
        if not r.content.startswith(PNG_MAGIC):
            fail(f"review-sheet {label}: not a PNG")
        print(f"review-sheet {label} ok ({len(r.content)} bytes)")

    r = client.get(f"/skins/submissions/{armor_id}/review-sheet")
    if r.status_code != 401:
        fail(f"review-sheet without key expected 401, got {r.status_code}")

    # Approve both
    for sid in (armor_id, large_id):
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
    if large_id not in by_id:
        fail("large missing from plugin approved list")
    if by_id[large_id].get("grip_preset") != "bottom":
        fail("large grip_preset missing on approved list")
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

    print("ALL OK — Step 2 smoke passed")
    sys.exit(0)


if __name__ == "__main__":
    main()
