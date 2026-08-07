# 01 — Current state (`dev`)

Honest baseline of ProvinceSystem on the **`dev`** branch. Planning and implementation should assume this tree, not `main`.

`main` still reflects older patterns (generators copying into `frontend/public/data`, Docker `npm run dev`). `dev` left that behind.

## Stack

| Layer | Tech |
|-------|------|
| Frontend | Next.js (App Router), React, Tailwind — production Docker (`npm run start`) |
| Backend | FastAPI + Uvicorn, Pillow mapgen |
| Deploy | `docker-compose.yml` — backend `:8000`, frontend `:3000` |
| Data | Per-map folders under `input/`, `defines/`, generated `output/` |

## Architecture today

```text
SimpleFactions (plugin)
        │  POST queue / upload JSON, GET regenerate
        ▼
FastAPI ── mapgen/regiongen ──► backend/src/output/{map}/…
        │
        │  FileResponse (maps, regions, banners)
        ▼
Next.js MapViewer  ◄── NEXT_PUBLIC_API_URL
```

- Generators **do not** write into `frontend/public`. Any leftover comments or mental models about that are obsolete.
- Assets are served by [`backend/src/api/file_routes.py`](../backend/src/api/file_routes.py).
- Paths are centralized in [`backend/src/scripts/util/dirs.py`](../backend/src/scripts/util/dirs.py).

## Frontend

| Path | Role |
|------|------|
| [`frontend/app/page.tsx`](../frontend/app/page.tsx) | Redirects to `/map/main` |
| [`frontend/app/map/main/page.tsx`](../frontend/app/map/main/page.tsx) | Calavorn map (`mapId="main"`) |
| [`frontend/app/map/r3b1rth/page.tsx`](../frontend/app/map/r3b1rth/page.tsx) | Second map route |
| [`frontend/app/components/MapViewer.tsx`](../frontend/app/components/MapViewer.tsx) | Almost all UI (author note: needs splitting) |
| [`frontend/app/core/MapEngineContext.tsx`](../frontend/app/core/MapEngineContext.tsx) | Layer visibility / drill-down |
| [`frontend/app/hooks/`](../frontend/app/hooks/) | Hover, coords, mode data, guild cache |

API base: `process.env.NEXT_PUBLIC_API_URL` (not committed; must be set for build/runtime).

There is **no site hub**, **no `/skins` route**, and **no shared layout nav** beyond what lives inside `MapViewer`.

## Backend API (mounted in `server.py`)

| Router | Examples |
|--------|----------|
| `map_routes` | `/{map}/map`, province lookup / meta |
| `data_routes` | compiled province data, defines JSON, upload |
| `file_routes` | mapdata, region overlays, banners |
| `banner_routes` | random banner generator |
| `claim_routes` | queue upload behind hashed key |
| `regen_routes` | map regeneration behind hashed key |

Auth today: hardcoded secret → MD5 → path segment on claim/regen only ([`auth.py`](../backend/src/scripts/util/auth.py)). Other endpoints (including some uploads) are open. Acceptable for low-value map data; skins will need tighter handling for codes and files.

## Map pipeline

- **Input:** `backend/src/input/{main,dev}/` (nation JSON, provinces.png, queue, …)
- **Defines:** `backend/src/defines/{main,dev}/` (compiled nation/county/… JSON)
- **Output:** `backend/src/output/{map}/maps|regions|banners/` — **gitignored**, produced by regen

Generators on `dev` paint pixels directly (no flood-fill in the hot path). Region overlays are still **full-map-sized** transparent PNGs. The browser stacks one `<img>` per visible region — main runtime cost.

Docker mounts `input`, `defines`, and `output` into the backend container so regen persists on the host.

## What works

- Multi-map nation / county / duchy / kingdom / empire (and extra modes on `dev` such as terrain, fertility, trade, prosperity where data exists)
- Drill-down subjects, hover overlays, banners, vote links, Discord invite
- Plugin-driven queue + regenerate for live border updates
- Production-oriented compose (no live frontend source mount)

## Known issues (map / UX)

1. **Realm size on hover card** — `calculate_size` in [`nation_compiler.py`](../backend/src/scripts/compile/nation_compiler.py) is correct on `dev`. [`useRegionHover.ts`](../frontend/app/hooks/useRegionHover.ts) does **not** pass `size`, `subject_size`, `subjects`, or `overlord` into the card state. UI still expects those fields → looks “broken” even when JSON is fine.
2. **Runtime map performance** — full-canvas region PNGs × N visible nations; `getImageData` on mousemove for region modes; terrain/fertility/prosperity modes hit the API on hover.
3. **Mobile** — desktop `flex-row` layout; no serious responsive pass.
4. **Local demo friction** — empty `output/` until you regen; `NEXT_PUBLIC_API_URL` easy to forget; compose always builds Next for production (slow UI iteration).
5. **Monolith UI** — `MapViewer` owns header, hero, map, side panels; hard to add skins as a peer feature.

## What does not exist yet

- Skins / texture submission
- Code / token redeem flow
- SQLite (or any app DB)
- Discord bot integration (approve / deny)
- Resource-pack bridge beyond the existing map JSON/regen path
- Modular frontend shell

## Implications for the roadmap

Stabilize and speed the map first (users already depend on it), introduce a thin site shell, document local run, then build skins as a separate backend+frontend module with clear contracts for the external Discord bot and Minecraft plugin.
