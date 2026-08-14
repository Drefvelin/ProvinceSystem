# 06 — Local development (no plugin / no Discord)

Goal: run pieces of the TFMC platform on a workstation. Full journeys: [12-end-to-end-flows.md](./12-end-to-end-flows.md).

## Full-stack local modes

| Mode | What you run | Good for |
|------|----------------|----------|
| **Website only** | ProvinceSystem backend + frontend (+ regen `output/`) | Map UI, skins API/UI with mock codes |
| **Website + bot** | Above + Red/`tfmc_bot` against local API | Discord skins approve/deny, ban role tests |
| **Website + test Paper** | Above + local/test server with SimpleFactions and/or ArmourShop pointed at local API | Map upload/regen; skins code mint + pack write into a **copy** of IA contents |
| **Production-like** | Docker compose for ProvinceSystem; plugins on real host | Final integration |
| **AMP-host staging** | Separate clone + [STAGING.md](../STAGING.md) (`18001`/`13001`) | Discord bot vs localhost API without touching prod |

Most day-to-day UI work is **website only**. Do not require Paper to start Sprint S1–S2.

## What you already have on `dev`

| Path | Role |
|------|------|
| `backend/src/input/{main,dev}/` | Sample worlds (nation JSON, `map.png` Xaero plain export, `provinces.png`, …) |
| `backend/src/defines/{main,dev}/` | Compiled / static defines |
| `backend/src/output/` | **Generated** maps/regions/banners — gitignored, often empty until regen; `fullregen` also writes `maps/parchment_base.png` from `map.png` |
| `docker-compose.yml` | Backend + frontend prod images; volumes for input/defines/output |

The live Minecraft plugins are **not** required to view maps or develop the skins web/API. SimpleFactions refreshes live faction data; ArmourShop later mints codes and applies packs.

## Prerequisites

- Docker + Docker Compose  
- Or: Python 3.10+ with `backend/requirements.txt`, and Node 22+ for frontend  
- Env: **`NEXT_PUBLIC_API_URL`** must point at the API the browser will call (e.g. `http://localhost:8000`)

Note: Next bakes `NEXT_PUBLIC_*` at **build** time for the Docker frontend image. Set the build arg/env when building the frontend, or use a local `next dev` override for UI work.

## Path A — Docker (closest to prod)

From `ProvinceSystem/`:

```bash
docker compose build
docker compose up -d
```

Then:

1. Ensure `output/` has images (see **Generate output** below). If empty, maps 404.
2. Open `http://localhost:3000` (redirects to `/map/main`).
3. API health: `http://localhost:8000/ping`

Useful reset (from [`docker_run.txt`](../docker_run.txt)):

```bash
docker compose down --volumes --remove-orphans
docker compose build --no-cache
docker compose up -d --force-recreate
```

Volumes keep host `input` / `defines` / `output` in sync with the container.

## Path B — Backend local + frontend local (fast UI iteration)

**Backend** (from `backend/`):

```bash
pip install -r requirements.txt
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend** (from `frontend/`):

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000

npm ci
npm run dev
```

Open `http://localhost:3000`. Prefer this while editing React/CSS.

Optional later: `docker-compose.override.yml` that runs the frontend with `npm run dev` and a bind mount — not required for MVP docs.

## Generate output (required once per machine / after generator changes)

Without `output/{map}/maps/…` and region PNGs, the UI has nothing to show.

Trigger a full regen the same way production does (hashed key from [`auth.py`](../backend/src/scripts/util/auth.py) — local secret is fine for demo):

```text
GET http://localhost:8000/{map}/{hashed_key}/api/regenerate/fullregen
```

Example maps on this repo: `main`, `dev`.

Or call the regeneration entrypoint from a small Python script / REPL using `run_regeneration` for the map you care about (see `regen_routes` / `regeneration` util).

After **cropped overlay** work lands ([04-map-performance.md](./04-map-performance.md)), run **fullregen** again so bboxes and small PNGs exist.

## Smoke checklist (map)

- [ ] `GET /ping` → ok  
- [ ] `/map/main` loads base map + overlays  
- [ ] Map mode dropdown switches  
- [ ] Hover shows region name; realm size appears after Phase 1 fix  
- [ ] No plugin running  

## Skins without ArmourShop / Discord (Track B1+)

1. Mount or create `backend/src/data/` (and compose volume when using Docker).  
2. Run migrations; seed a code:

   - Pick a fake UUID  
   - Insert `code_hash` for a known plaintext like `TEST-CODE-1`  
3. Open `/skins`, redeem, submit with a valid **slug** (e.g. `blue_knight`) — see [07-naming-conventions.md](./07-naming-conventions.md).  
4. Fixture uploads (**exact pixel sizes** required; OS picker names ignored):

   - **item** / **handheld:** one **16×16** PNG → `{slug}.png`  
   - **large_handheld:** one **32×32** PNG + `grip_preset` (`bottom`|`middle`|`top`) → `{slug}.png`  
   - **armor_set:** four **16×16** icons + two **64×32** layers → `{slug}_helmet.png`, `_chestplate`, `_leggings`, `_boots`, `_layer_1`, `_layer_2`  

5. Fetch staff review sheet (optional for curl MVP):

```bash
curl -o sheet.png http://localhost:8000/skins/submissions/{id}/review-sheet \
  -H "X-Staff-Key: …"
```

6. Approve with curl + staff key:

```bash
curl -X POST http://localhost:8000/skins/submissions/{id}/approve \
  -H "X-Staff-Key: …"
```

7. Exercise `GET /skins/plugin/approved` with the plugin key; no Java required for API testing.

### ArmourShop / ItemsAdder later

Pack writes are tested against a **copy** of ItemsAdder contents (e.g. from `ItemsAdder Copy`), not production, until ArmourShop apply sprint. Point ArmourShop config at that copy locally if you need a dry run ([10](./10-armourshop-itemsadder.md)).

### Bot (Step 4)

- Cogs live in `tfmc_bot/` as **[Red-DiscordBot](https://github.com/cog-creators/red-discordbot)** cogs; production Red runs on **AMP (CubeCoders)**.
- For skins review: set `API_BASE_URL` to your **local/staging** API (not required to touch live website), `STAFF_KEY`, and `BOT_FEED_CHANNEL_ID` for **`#bot-feed`**.
- Create pending submissions via local `/skins` or curl; cog posts raw PNGs and approve/deny. See [11](./11-discord-bot.md) and [batches/step-4](./batches/step-4/00-index.md).
- Ban-role updates are a later track; not required for skins Discord MVP.

### SimpleFactions later

Point `RestServer.apiURL` / config at `http://localhost:8000` and use a test `mapRef` ([09](./09-map-system.md)).

## CORS / URLs

[`server.py`](../backend/server.py) allows `http://localhost:3000` and the production TFMC origins. If you use another host port, add it to CORS or use localhost as above.

## What not to expect locally

- Live SimpleFactions border pushes (unless you point a test server at your API)  
- Real donator codes from ArmourShop  
- Discord buttons  
- Writing into the live Paper ItemsAdder folder / pack reload  

Those are integration environments; website-only is for **look and feel + API correctness**. Follow [08-implementation-checklist.md](./08-implementation-checklist.md) for the full platform path.

## Doc upkeep

When compose, env, or regen URLs change, update this file in the same PR. Link to it from the root README when the team is ready (optional follow-up).
