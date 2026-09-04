# Local development

Goal: run pieces of the TFMC platform on a workstation. Full journeys: [flows/journeys.md](../flows/journeys.md).

## Full-stack local modes

| Mode | What you run | Good for |
|------|----------------|----------|
| **Website only** | ProvinceSystem backend + frontend (+ regen `output/`) | Map UI, skins API/UI with mock codes |
| **Website + bot** | Above + Red/`tfmc_bot` against local API | Discord skins/drinks approve/deny, ban role tests |
| **Website + test Paper** | Above + local/test server with SimpleFactions and/or ArmourShop pointed at local API | Map upload/regen; skins code mint + pack write into a **copy** of IA contents |
| **Production-like** | Docker compose for ProvinceSystem; plugins on real host | Final integration |
| **AMP-host staging** | Separate clone + [STAGING.md](../../STAGING.md) (`18001`/`13001`) | Discord bot vs localhost API without touching prod |

Most day-to-day UI work is **website only**. Paper is not required to start map or skins UI work.

## What you already have on `dev`

| Path | Role |
|------|------|
| `backend/src/input/{main,dev}/` | Sample worlds (nation JSON, `map.png` Xaero plain export, `provinces.png`, …) |
| `backend/src/defines/{main,dev}/` | Compiled / static defines |
| `backend/src/output/` | **Generated** maps/regions/banners - gitignored, often empty until regen; `fullregen` also writes `maps/parchment_base.png` from `map.png` |
| `docker-compose.yml` | Backend + frontend prod images; volumes for input/defines/output |

The live Minecraft plugins are **not** required to view maps or develop the skins web/API. SimpleFactions refreshes live faction data; ArmourShop mints codes and applies packs in integration environments.

## Prerequisites

- Docker + Docker Compose  
- Or: Python 3.10+ with `backend/requirements.txt`, and Node 22+ for frontend  
- Env: **`NEXT_PUBLIC_API_URL`** must point at the API the browser will call (e.g. `http://localhost:8000`)

Note: Next bakes `NEXT_PUBLIC_*` at **build** time for the Docker frontend image. Set the build arg/env when building the frontend, or use a local `next dev` override for UI work.

## Path A - Docker (closest to prod)

From `ProvinceSystem/`:

```bash
docker compose build
docker compose up -d
```

Then:

1. Ensure `output/` has images (see **Generate output** below). If empty, maps 404.
2. Open `http://localhost:3000` (redirects to `/map/main`).
3. API health: `http://localhost:8000/ping`

Useful reset (from [`docker_run.txt`](../../docker_run.txt)):

```bash
docker compose down --volumes --remove-orphans
docker compose build --no-cache
docker compose up -d --force-recreate
```

Volumes keep host `input` / `defines` / `output` in sync with the container.

## Path B - Backend local + frontend local (fast UI iteration)

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

## Generate output (required once per machine / after generator changes)

Without `output/{map}/maps/…` and region PNGs, the UI has nothing to show.

Trigger a full regen the same way production does (hashed key from [`auth.py`](../../backend/src/scripts/util/auth.py) - local secret is fine for demo):

```text
GET http://localhost:8000/{map}/{hashed_key}/api/regenerate/fullregen
```

Example maps on this repo: `main`, `dev`.

After **cropped overlay** generator changes, run **fullregen** again so bboxes and small PNGs exist. See [map/viewer.md](../map/viewer.md).

If a **public** data route answers `404 {"detail": "Artifact not found"}` - `/{map}/data/province_id_runs` or `/{map}/data/province_id_grid_q4` - the geometry artifact has not been built for that map. Build it with:

```text
python -m src.scripts.tools.build_province_id_grid --map {map}
```

run from `backend/`. The 404 body deliberately does not name this command: those two routes need no authentication, and an unauthenticated caller should not be handed its own input back plus a module path to run. The staff-gated editor equivalents (`/{map}/editor/province-runs`, `/{map}/editor/province-grid`) still print the command in their 404, because their caller is already authenticated as staff.

## Smoke checklist (map)

- [ ] `GET /ping` → ok  
- [ ] `/map/main` loads base map + overlays  
- [ ] Map mode dropdown switches  
- [ ] Hover shows region name; realm size appears when data exists  
- [ ] No plugin running  

## Skins without ArmourShop / Discord

1. Mount or create `backend/src/data/` (and compose volume when using Docker).  
2. Run migrations; seed a code (see [dev-config.md](./dev-config.md) for `seed_dev_code.py`).  
3. Open `/skins`, redeem, submit with a valid item name - see [cosmetics/naming.md](../cosmetics/naming.md).  
4. Fixture uploads (**exact pixel sizes** required; OS picker names ignored):

   - **handheld:** one **16×16** PNG  
   - **large_handheld:** one **32×32** PNG + `grip_preset` (`bottom`|`middle`|`top`)  
   - **armor_set:** four **16×16** icons + two **64×32** layers per tier  

5. Fetch staff review sheet (optional for curl MVP):

```bash
curl -o sheet.png http://localhost:8000/skins/submissions/{id}/review-sheet \
  -H "X-Staff-Key: …"
```

For **3D kinds** (`item_3d`, `shield`, `gun`, …), install the sheet renderer once on the API host ([sheet-render.md](./sheet-render.md)):

```bash
cd backend/render && npm install && npx playwright install chromium
```

Without Node/Playwright, the sheet is texture-only; staff Discord posts show a **3D preview** error field.

6. Approve with curl + staff key:

```bash
curl -X POST http://localhost:8000/skins/submissions/{id}/approve \
  -H "X-Staff-Key: …"
```

7. Exercise `GET /skins/plugin/approved` with the plugin key; no Java required for API testing.

### ArmourShop / ItemsAdder later

Pack writes are tested against a **copy** of ItemsAdder contents (e.g. from `ItemsAdder Copy`), not production. Point ArmourShop config at that copy locally if you need a dry run ([integrations/armourshop.md](../integrations/armourshop.md)).

### Bot

- Cogs live in `tfmc_bot/` as **[Red-DiscordBot](https://github.com/cog-creators/red-discordbot)** cogs; production Red runs on **AMP (CubeCoders)**.
- For skins/drinks review: set `API_BASE_URL` to your **local/staging** API, `STAFF_KEY`, and `BOT_FEED_CHANNEL_ID` for **`#bot-feed`**.
- Create pending submissions via local `/skins` or curl; cog posts review embeds. See [integrations/discord-bot.md](../integrations/discord-bot.md) and [tfmc_bot/docs/local-dev.md](../../../tfmc_bot/docs/local-dev.md).

### SimpleFactions later

Point TFMCWeb `api.base-url` at `http://localhost:8000` and use a test `mapRef` ([integrations/simplefactions.md](../integrations/simplefactions.md)).

## CORS / URLs

[`server.py`](../../backend/server.py) allows `http://localhost:3000` and the production TFMC origins. If you use another host port, add it to CORS or use localhost as above.

## What not to expect locally

- Live SimpleFactions border pushes (unless you point a test server at your API)  
- Real donator codes from ArmourShop (use TFMCWeb on a test server, or seed codes)  
- Discord buttons (unless bot is running against your API)  
- Writing into the live Paper ItemsAdder folder / pack reload  

Those are integration environments; website-only is for **look and feel + API correctness**.

## Dev config reference

Dev-only flags, spoof data, and UI dev shortcuts: [dev-config.md](./dev-config.md).
