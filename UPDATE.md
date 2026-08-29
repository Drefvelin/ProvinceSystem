# Production deploy (AMP host)

**Product docs:** [docs/README.md](./docs/README.md)

ProvinceSystem on the live box uses **production ports** only:

| Service | Host port | Container | Public URL (nginx) |
|---------|-----------|-----------|-------------------|
| API | **8000** | 8000 | `https://www.tfminecraft.net/api/` |
| UI (Next.js) | **3000** | 3000 | `https://www.tfminecraft.net/` |

Plugins, Red bot, and MC servers on the same host talk to the API at **`http://127.0.0.1:8000`** (not 18001).

**Staging** (optional, separate clone) uses **18001** / **13001** via `docker-compose.staging.yml` — see [STAGING.md](./STAGING.md) and section 6 below. Do **not** use staging scripts for production deploy.

---

## Important: run compose from the repo root

All `docker compose` commands must run from **`~/ProvinceSystem`** (the directory that contains `docker-compose.yml`), **not** from `~/ProvinceSystem/frontend`.

```bash
cd ~/ProvinceSystem
docker compose build --no-cache
docker compose up -d
```

---

## 1. Purge the old production stack

If old `provincesystem-*` containers are still running:

```bash
docker stop provincesystem-frontend-1 provincesystem-backend-1 2>/dev/null || true
docker rm provincesystem-frontend-1 provincesystem-backend-1 2>/dev/null || true
```

Or from the old compose directory:

```bash
docker inspect provincesystem-backend-1 --format '{{index .Config.Labels "com.docker.compose.project.working_dir"}}'
cd <that-directory>
docker compose down
```

Confirm ports **8000** and **3000** are free:

```bash
sudo ss -tlnp | grep -E ':8000|:3000'
```

---

## 2. Purge the staging stack (18001 / 13001)

Only if `tfmc-staging-*` containers are still up:

```bash
cd ~/tfmc-staging   # or wherever the staging clone lives
docker compose -f docker-compose.staging.yml down --rmi local
```

Optional aggressive cleanup:

```bash
docker compose -f docker-compose.staging.yml down --rmi local --volumes
```

Confirm staging ports are gone:

```bash
sudo ss -tlnp | grep -E ':18001|:13001'
```

---

## 3. One-time production setup

### 3a. `backend/.env` (required)

`docker-compose.yml` loads **`backend/.env`** into the API container. Create it on the server before the first `docker compose up` (file is gitignored):

```bash
cd ~/ProvinceSystem
nano backend/.env
```

Example (use your real production keys):

```env
PS_PRODUCTION=1
PLUGIN_KEY=your-production-plugin-key
STAFF_KEY=your-production-staff-key
MINESKIN_API_KEY=your-mineskin-api-key
```

- `PS_PRODUCTION=1` enables the production startup guard. See [docs/identity/auth-security.md](./docs/identity/auth-security.md).
- `PLUGIN_KEY` must match TFMCWeb `api.plugin-key` on every MC server.
- `STAFF_KEY` must match Red bot `staff_key` in skinsreview / drinksreview / minecraftban.
- Do **not** set `SKINS_DEV=1` or `CHARACTER_UI_DEV=1` on production.

If `backend/.env` is missing, compose may warn or the backend may start without keys.

### 3b. Do not let `frontend/.env` override the public API URL

The Docker build log may show `Environments: .env`. If **`frontend/.env`** exists on the server with:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

that value is baked into the client bundle and causes:

- API calls from browsers to hit **localhost** (broken for visitors)
- Chrome "use other apps on this device" permission prompts

**Production:** either delete `frontend/.env` on the server, or set:

```env
NEXT_PUBLIC_API_URL=https://www.tfminecraft.net/api
```

The compose file also passes `NEXT_PUBLIC_API_URL` as a Docker build arg; avoid conflicting `frontend/.env` values.

### 3c. Data directories

Ensure `backend/src/data`, `input`, `output`, and `defines` exist and contain the data you need (copy from the old stack if migrating).

---

## 4. Production deploy / redeploy

SSH in, then from **`~/ProvinceSystem`**:

```bash
cd ~/ProvinceSystem
git fetch origin
git checkout main
git reset --hard origin/main
docker compose down
docker compose build --no-cache
docker compose up -d
```

```bash
docker compose logs -f backend --since 1m
```

**Do not** run `./scripts/staging-*.sh` for production. Those only apply to `docker-compose.staging.yml` (ports 18001/13001).

If `docker compose build` fails, fix the error and rebuild. Do not run `up` expecting a new frontend image until the build succeeds.

Smoke checks on the host:

```bash
curl -s http://127.0.0.1:8000/ping
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3000/
```

Expected: `{"ok":true}` and HTTP `200`.

Public check (after nginx):

```bash
curl -s https://www.tfminecraft.net/api/ping
```

### Optional: Season 5 dev landing

Production `docker-compose.yml` enables the gate by default (`NEXT_PUBLIC_SITE_DEV_GATE=1` build arg).

**Launch day:** set the build arg to `"0"` (or remove the line), then rebuild the frontend:

```bash
docker compose build --no-cache frontend
docker compose up -d
```

---

## 5. nginx (`/etc/nginx/sites-enabled/tfminecraft.net`)

Existing layout is correct. No new `location` blocks needed.

| Location | Upstream | Purpose |
|----------|----------|---------|
| `/` | `127.0.0.1:3000` | Next.js UI |
| `/api/` | `127.0.0.1:8000/` | ProvinceSystem API |
| `/restart`, `/api/restart` | `127.0.0.1:8001` | Unrelated restart service |

**Recommended:** expand CORS methods on `/api/`:

```nginx
add_header Access-Control-Allow-Methods "GET, POST, PUT, PATCH, DELETE, OPTIONS" always;
```

The new site uses PUT, PATCH, and DELETE (character editor, map editor, logout).

After edits:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

---

## 6. Same-host integrations

| Component | Setting | Value |
|-----------|---------|-------|
| TFMCWeb | `api.base-url` | `http://127.0.0.1:8000` |
| TFMCWeb | `api.plugin-key` | same as `PLUGIN_KEY` in `backend/.env` |
| Red `skinsreview` | `api_base_url` | `http://127.0.0.1:8000` |
| Red `drinksreview` | `api_base_url` | `http://127.0.0.1:8000` |
| Red `minecraftban` | `api_base_url` | `http://127.0.0.1:8000` |
| SimpleFactions | (none) | Uses TFMCWeb gateway |

TFMCWeb and SimpleFactions must use **loopback** API URLs on the game host, not the public site hostname. See [docs/integrations/simplefactions.md](./docs/integrations/simplefactions.md).

---

## 7. Staging stack (optional, later)

Only for a **separate** test clone (`~/tfmc-staging`), not the live `~/ProvinceSystem` deploy:

```bash
cd ~/tfmc-staging
git fetch origin && git checkout main && git reset --hard origin/main
chmod +x scripts/staging-*.sh
./scripts/staging-down.sh
./scripts/staging-up.sh
curl -s http://127.0.0.1:18001/ping
```

Full checklist: [STAGING.md](./STAGING.md).

---

## Troubleshooting

| Symptom | Likely cause |
|---------|----------------|
| Build fails at `npm run build` | Pull latest code; TypeScript errors must be fixed before deploy |
| Chrome asks to use apps on device | Frontend built with `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000` — fix `frontend/.env` or rebuild with compose build arg |
| `env_file` / missing keys | Create `backend/.env` with `PLUGIN_KEY` and `STAFF_KEY` |
| API 401 from bot / TFMCWeb | Keys in `backend/.env` do not match plugin/bot configs |
| `version` obsolete warning | Harmless; removed from `docker-compose.yml` in newer commits |

---

## Notes

- `git reset --hard` does not delete `backend/.env` if it is gitignored and already on disk.
- Does **not** update Paper jars (TFMCWeb, ArmourShop, etc.) — deploy those via AMP separately.
