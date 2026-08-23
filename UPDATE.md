# Production deploy (AMP host)

ProvinceSystem on the live box uses **production ports** only:

| Service | Host port | Container | Public URL (nginx) |
|---------|-----------|-----------|-------------------|
| API | **8000** | 8000 | `https://www.tfminecraft.net/api/` |
| UI (Next.js) | **3000** | 3000 | `https://www.tfminecraft.net/` |

**Staging** (optional side stack) uses **18001** / **13001** via `docker-compose.staging.yml` — see [STAGING.md](./STAGING.md). Retire it when production replaces the old site.

Plugins, Red bot, and MC servers on the same host talk to the API at **`http://127.0.0.1:8000`** (not 18001).

---

## 1. Purge the old production stack (7-month `provincesystem-*` containers)

Find the compose project directory (if unsure):

```bash
docker inspect provincesystem-backend-1 --format '{{index .Config.Labels "com.docker.compose.project.working_dir"}}'
```

Stop and remove the old stack:

```bash
cd <that-directory>
docker compose down
```

Or stop by container name from anywhere:

```bash
docker stop provincesystem-frontend-1 provincesystem-backend-1
docker rm provincesystem-frontend-1 provincesystem-backend-1
```

Optional: remove old images

```bash
docker image prune -f
```

Confirm ports **8000** and **3000** are free before deploying:

```bash
sudo ss -tlnp | grep -E ':8000|:3000'
```

---

## 2. Purge the staging stack (`tfmc-staging-*` on 18001 / 13001)

From your staging clone (`~/tfmc-staging`, `~/ProvinceSystem`, etc.):

```bash
cd ~/tfmc-staging   # adjust path
chmod +x scripts/staging-*.sh
./scripts/staging-down.sh
```

Aggressive cleanup (removes staging containers, local images, and named volumes for that compose file):

```bash
docker compose -f docker-compose.staging.yml down --rmi local --volumes
```

Confirm staging ports are gone:

```bash
sudo ss -tlnp | grep -E ':18001|:13001'
docker ps --filter name=tfmc-staging
```

You can keep the git clone for future testing or delete the folder. Production no longer needs `site-rework` running beside prod.

**Point integrations at prod:** after purge, update TFMCWeb `api.base-url` and Red bot `api_base_url` to `http://127.0.0.1:8000` (see section 5).

---

## 3. Production deploy (`docker-compose.yml`)

### One-time server setup

1. Clone or use existing repo path (e.g. `~/ProvinceSystem`).
2. Create **`backend/.env`** on the server (gitignored). Production example:

```bash
# backend/.env — do NOT commit
PLUGIN_KEY=<match TFMCWeb api.plugin-key>
STAFF_KEY=<match Red bot staff_key>
MINESKIN_API_KEY=<if used>
# Do not set SKINS_DEV=1 on production
```

3. Ensure data volumes exist under `backend/src/data`, `input`, `output`, `defines` (migrate/import from old stack if needed).

### Deploy / redeploy

SSH in, `cd` to the production clone, then:

```bash
git fetch origin
git checkout main
git reset --hard origin/site-rework
chmod +x scripts/staging-*.sh
docker compose down
docker compose build --no-cache
docker compose up -d --force-recreate
```

Smoke checks on the host:

```bash
curl -s http://127.0.0.1:8000/ping
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3000/
```

Expected: `{"ok":true}` and HTTP `200` from the UI.

Public checks (after nginx):

```bash
curl -s https://www.tfminecraft.net/api/ping
```

### Frontend build args

`docker-compose.yml` bakes **`NEXT_PUBLIC_API_URL=https://www.tfminecraft.net/api`** at build time so browser calls go through nginx `/api/` to the backend.

Optional env on the frontend service (uncomment in compose when needed):

```yaml
- NEXT_PUBLIC_SITE_DEV_GATE=1   # Season 5 dev landing; staff code + tfmc.map.staff
```

Rebuild the frontend after changing any `NEXT_PUBLIC_*` value.

---

## 4. nginx (`/etc/nginx/sites-enabled/tfminecraft.net`)

Your existing layout is correct for the new site. No new `location` blocks are required.

| Location | Upstream | Purpose |
|----------|----------|---------|
| `/` | `127.0.0.1:3000` | Next.js UI (/, /map, /skins, /drinks, /character, …) |
| `/api/` | `127.0.0.1:8000/` | ProvinceSystem API (`/api/ping` → backend `/ping`, `/api/skins/...` → `/skins/...`) |
| `/restart`, `/api/restart` | `127.0.0.1:8001` | Unrelated restart service — leave as-is |

**Recommended change:** expand CORS methods on `/api/`. The new site uses **PUT**, **PATCH**, and **DELETE** (character editor, map editor, logout, etc.). Update:

```nginx
add_header Access-Control-Allow-Methods "GET, POST, PUT, PATCH, DELETE, OPTIONS" always;
```

**Optional cleanup:** FastAPI already sets CORS in `backend/server.py` for `https://www.tfminecraft.net`. You can remove the four `add_header Access-Control-*` lines from the `/api/` block and let the backend handle CORS to avoid duplicate headers.

After edits:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

---

## 5. Same-host integrations (after port change)

| Component | Setting | Value |
|-----------|---------|-------|
| TFMCWeb | `api.base-url` | `http://127.0.0.1:8000` |
| TFMCWeb | `api.plugin-key` | same as `PLUGIN_KEY` in `backend/.env` |
| Red `skinsreview` | `api_base_url` | `http://127.0.0.1:8000` |
| Red `drinksreview` | `api_base_url` | `http://127.0.0.1:8000` |
| Red `minecraftban` | `api_base_url` | `http://127.0.0.1:8000` |
| SimpleFactions | (none) | Uses TFMCWeb gateway — no direct API URL |

Reload TFMCWeb (`/web reload` or restart) and Red cogs (`-reload …`).

---

## 6. Staging stack (optional, later)

Only if you need a side-by-side test clone again:

```bash
cd ~/tfmc-staging
git fetch origin && git checkout site-rework && git reset --hard origin/site-rework
./scripts/staging-down.sh && ./scripts/staging-up.sh
curl -s http://127.0.0.1:18001/ping
```

Browser from your PC (SSH tunnel):

```bash
ssh -L 13001:127.0.0.1:13001 -L 18001:127.0.0.1:18001 tfmc@188.40.119.246
```

- UI: http://127.0.0.1:13001
- API: http://127.0.0.1:18001

Full staging checklist: [STAGING.md](./STAGING.md).

---

## Notes

- `reset --hard` drops local edits on the server clone. Re-create `backend/.env` if it lived only in the repo tree and was wiped (it should live only on the server, outside git).
- Does **not** update Paper jars (TFMCWeb, ArmourShop, etc.) — deploy those via AMP separately.
- Old stack container names: `provincesystem-*`. New stack uses the compose project name from the directory (often `provincesystem` if the folder name matches).
