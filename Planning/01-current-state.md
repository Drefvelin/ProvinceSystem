# 01 — Current state (`dev`)

Honest baseline of ProvinceSystem on the **`dev`** branch (2026). Planning and implementation should assume this tree, not `main`.

## Stack

| Layer | Tech |
|-------|------|
| Frontend | Next.js (App Router), React, Tailwind — production Docker (`npm run start`) |
| Backend | FastAPI + Uvicorn, Pillow mapgen, SQLite (skins, drinks, characters, identity) |
| Deploy | `docker-compose.yml` — backend `:8000`, frontend `:3000` |
| Data | Per-map folders under `input/`, `defines/`, generated `output/`; `backend/src/data/` for app DB + uploads |

## Architecture today

```text
SimpleFactions (plugin)
        │  POST queue / upload JSON, GET regenerate
        ▼
FastAPI ── mapgen/regiongen ──► backend/src/output/{map}/…
        │  skins / drinks / characters / identity APIs
        ▼
Next.js  ◄── hub, /map, /skins, /drinks, /character
```

- Generators **do not** write into `frontend/public`.
- Assets served by [`backend/src/api/file_routes.py`](../backend/src/api/file_routes.py).
- Paths centralized in [`backend/src/scripts/util/dirs.py`](../backend/src/scripts/util/dirs.py).

## Frontend

| Path | Role |
|------|------|
| [`frontend/app/page.tsx`](../frontend/app/page.tsx) | TFMC hub landing |
| [`frontend/app/map/main/page.tsx`](../frontend/app/map/main/page.tsx) | Calavorn map (`mapId="main"`) |
| [`frontend/app/map/r3b1rth/page.tsx`](../frontend/app/map/r3b1rth/page.tsx) | Dev map (URL-only, not in nav) |
| [`frontend/app/skins/`](../frontend/app/skins/) | Skins redeem, upload, status |
| [`frontend/app/drinks/`](../frontend/app/drinks/) | Drink brew form |
| [`frontend/app/character/`](../frontend/app/character/) | Character creator + kits + wardrobe |
| [`frontend/app/components/MapViewer.tsx`](../frontend/app/components/MapViewer.tsx) | Map composer; UI in [`components/map/`](../frontend/app/components/map/) |
| [`frontend/app/components/shell/SiteHeader.tsx`](../frontend/app/components/shell/SiteHeader.tsx) | Shared nav |

API base: `process.env.NEXT_PUBLIC_API_URL`.

## Backend API (high level)

| Area | Examples |
|------|----------|
| Map | `map_routes`, `data_routes`, `file_routes`, `regen_routes` |
| Skins | codes, redeem, upload, staff review, plugin approved |
| Drinks | redeem, submit, catalog, staff review |
| Characters | session, create, roster, wardrobe, `rpc_player_meta` |
| Identity | Discord link, guild grace |

Map regen auth: hashed key on claim/regen routes. Cosmetic routes use session tokens / plugin keys.

## What works (platform)

- Multi-map nation / county / duchy / kingdom / empire (+ terrain, fertility, trade, prosperity where data exists)
- Hub + `/skins` + `/drinks` + `/character` (creator, kits, sheet, wardrobe)
- TFMCWeb tokens, Discord link, shared skin↔drink cooldown, realm gateway (steps 32–35)
- Skins E2E path (upload → Discord → ArmourShop apply)
- Drinks E2E path (upload → Discord → DrinkBuilder apply)

## Known issues (map — primary remaining site work)

Product truth: [16-map-platform.md](./16-map-platform.md) · build [step-38](./batches/step-38/00-index.md)–[45](./batches/step-45/00-index.md). Step 37 (site UX, modal, drill, cropped overlays, mobile) **code done**.

1. **Visual** — flat RGB nation blobs; no parchment base from Xaero; no curved labels ([step-38](./batches/step-38/00-index.md)–[39](./batches/step-39/00-index.md)).
2. **Staff maps** — no per-mapId access gate ([step-40](./batches/step-40/00-index.md)).
3. **Settlements / forts / wars / chronicle / wealth** — not on map yet ([steps 41–45](./batches/step-45/00-index.md)).
4. **Cropped overlays** — require **fullregen** after deploy for bbox metadata ([03-cropped-overlays](./batches/step-37/03-cropped-overlays.md)).

## Implications for the roadmap

Cosmetics, characters, drinks, and TFMCWeb gateway are **shipped in code**. **Track H / map platform** (steps 36–45) is the primary remaining website work. See [03-roadmap.md](./03-roadmap.md).
