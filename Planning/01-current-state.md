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
- Desktop pan/zoom on `/map/{id}`: wheel zoom toward cursor, middle-mouse pan, clamped bounds ([step-49](./batches/step-49/00-index.md) — **code done**)
- Hub + `/skins` + `/drinks` + `/character` (creator, kits, sheet, wardrobe)
- TFMCWeb tokens, Discord link, shared skin↔drink cooldown, realm gateway (steps 32–35)
- Skins E2E path (upload → Discord → ArmourShop apply)
- Drinks E2E path (upload → Discord → DrinkBuilder apply)

## Known issues (map — primary remaining site work)

Product truth: [16-map-platform.md](./16-map-platform.md) · build [step-42](./batches/step-42/00-index.md)–[46](./batches/step-46/00-index.md). Steps 37–40 (site UX + parchment + ink cartography + nation labels) **code done**. Steps 47–49 (multi-mode labels, label neighbors, pan/zoom) **code done**. **Step 41** staff map access **code done** ([step-41](./batches/step-41/00-index.md)).

1. **Visual** — Nation labels shipped on `/map/main` nation mode ([step-40](./batches/step-40/00-index.md)); colour satellite base + parchment-wash overlays ([step-39](./batches/step-39/00-index.md)). Multi-mode title/trade labels + Calavorn terrain/fertility/trade/prosperity toolbar ([step-47](./batches/step-47/00-index.md) — **code done**). Desktop pan/zoom ([step-49](./batches/step-49/00-index.md) — **code done**). Further map layers: settlements, forts, wars, chronicle, wealth ([steps 42–46](./batches/step-46/00-index.md)).
2. **Settlements / forts / wars / chronicle / wealth** — not on map yet ([steps 42–46](./batches/step-46/00-index.md)) — **next: step 42**.
3. **Cropped overlays** — require **fullregen** after deploy for bbox metadata ([03-cropped-overlays](./batches/step-37/03-cropped-overlays.md)).

## Implications for the roadmap

Cosmetics, characters, drinks, and TFMCWeb gateway are **shipped in code**. **Track H / map platform** (steps 36–45) is the primary remaining website work. See [03-roadmap.md](./03-roadmap.md).
