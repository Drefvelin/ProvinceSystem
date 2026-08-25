# Staging stack (AMP host / SSH)

Temporary ProvinceSystem next to production for Discord bot and plugin integration testing. Uses ports **18001** (API) and **13001** (UI). Production `docker-compose.yml` (8000/3000) is unchanged.

Data lives only under this clone (`backend/src/data`, etc.).

**Product docs:** [docs/README.md](./docs/README.md) · **Flows:** [docs/flows/journeys.md](./docs/flows/journeys.md) · **Dev flags:** [docs/ops/dev-config.md](./docs/ops/dev-config.md)

## Prerequisites

- Docker + Docker Compose on the host
- Git access to this repo

## Update staging clone (every pull)

Staging boxes should track the remote branch **exactly**. Do **not** keep local edits (including `chmod +x` dirtying the scripts - that makes `git pull` fail with "local changes would be overwritten").

Use your staging path (`~/ProvinceSystem` or `~/tfmc-staging`). Checkout the branch you run on staging (**`site-rework`**). After `reset --hard`, always `chmod +x` again before running scripts.

```bash
cd ~/ProvinceSystem
git fetch origin
git checkout site-rework
git reset --hard origin/site-rework
chmod +x scripts/staging-*.sh
```

## Start (SSH)

First-time clone:

```bash
git clone <ProvinceSystem-git-url> ~/tfmc-staging
cd ~/tfmc-staging
git checkout site-rework
chmod +x scripts/staging-*.sh
./scripts/staging-down.sh
./scripts/staging-up.sh
curl -s http://127.0.0.1:18001/ping
```

`staging-down.sh` clears a failed partial up before `staging-up.sh`.

After later updates: use **Update staging clone** above, then:

```bash
./scripts/staging-down.sh
./scripts/staging-up.sh
curl -s http://127.0.0.1:18001/ping
```

Expected ping body: `{"ok":true}` (JSON). An HTML 404 means something else owns that port.

Stop later:

```bash
./scripts/staging-down.sh
```

## Same-host integrations

| Component | Setting | Value |
|-----------|---------|-------|
| TFMCWeb | `api.base-url` | `http://127.0.0.1:18001` (loopback only) |
| TFMCWeb | `api.plugin-key` | same as API `PLUGIN_KEY` |
| Red `skinsreview` | `api_base_url` | `http://127.0.0.1:18001` |
| Red `drinksreview` | `api_base_url` | `http://127.0.0.1:18001` |
| Red `minecraftban` | `api_base_url` | `http://127.0.0.1:18001` |
| SimpleFactions | (none) | Uses TFMCWeb gateway |

Loopback rule detail: [docs/integrations/simplefactions.md](./docs/integrations/simplefactions.md) · [docs/identity/auth-security.md](./docs/identity/auth-security.md)

## Red bot config

**`skinsreview` config.yml** (same machine as AMP/Red):

```yaml
api_base_url: "http://127.0.0.1:18001"
staff_key: "dev-staff-key"
bot_feed_channel_id: YOUR_BOT_FEED_CHANNEL_ID
poll_interval_seconds: 60
```

Set the same `api_base_url` and `staff_key` on **`drinksreview`** and **`minecraftban`**.

Then in Discord: `-reload skinsreview` → `/skinsreview ping`. Enable slash if needed: `!slash enable skinsreview` then `!slash sync`.

## Keys (compose defaults)

| Env | Value |
|-----|--------|
| `SKINS_DEV` | `1` |
| `STAFF_KEY` | `dev-staff-key` |
| `PLUGIN_KEY` | `dev-plugin-key` |

Override in `docker-compose.staging.yml` if you want stronger keys for a longer-lived staging box.

## Auth hardening

Full reference: [docs/identity/auth-security.md](./docs/identity/auth-security.md)

| Topic | Staging | Production |
|-------|---------|------------|
| `PS_PRODUCTION` | **Do not set** (staging keeps `SKINS_DEV=1`) | Set `PS_PRODUCTION=1` |
| Dev flags | `SKINS_DEV=1` OK | `SKINS_DEV` and `CHARACTER_UI_DEV` must be unset |
| API keys | Compose dev defaults OK | Real `PLUGIN_KEY` / `STAFF_KEY` required |
| Internal queue/regen | Callers use loopback `http://127.0.0.1:18001` | Same: never public hostname |
| Code inspect | Staff Bearer + `tfmc.map.staff` server-side | Same |
| Frontend build | `NEXT_PUBLIC_CHARACTER_UI_DEV` unset for prod images | Pass `PS_PRODUCTION=1` build arg when building prod frontend |

## Smoke checklist

Tick after a staging deploy or major pull. Detail for each flow: [docs/flows/journeys.md](./docs/flows/journeys.md).

### Stack

- [ ] `curl -s http://127.0.0.1:18001/ping` → `{"ok":true}`
- [ ] `http://127.0.0.1:13001/` loads hub

### Identity (TFMCWeb)

- [ ] `/linkdiscord` in-game → Discord `/linkdiscord <code>` completes bind
- [ ] Survival unlinked player frozen; non-Survival staff not gated
- [ ] Guild leave → ≤1h grace; rejoin clears; after expire → freeze

### Skins

- [ ] `/token create skin` → redeem on `/skins` → upload → `#bot-feed` approve → outcome DM
- [ ] Non-ranked player cannot mint; ranked KindPicker filtered by entitlements

### Drinks

- [ ] `/token create drink` → redeem on `/drinks` → submit → approve in Discord

### Characters

- [ ] `/token create character` → redeem on `/character` → create + list on site

### Map

- [ ] `/map/main` loads base map + overlays; hover and drill-down work
- [ ] Staff-only map returns 403 without `tfmc.map.staff`

### Staff tools

- [ ] Map title editor opens from **Edit titles** with staff session
- [ ] Code inspect requires staff Bearer + `tfmc.map.staff`

### Moderation

- [ ] `/warning` → in-game chat + Discord DM
- [ ] `/tempban` → Discord DM + Banned role; `/unban` clears role

### Auth / config

- [ ] TFMCWeb `api.base-url` is loopback (`127.0.0.1:18001`), not public hostname
- [ ] `PS_PRODUCTION` not set on staging

## SSH tunnel (test UI from your PC)

```bash
ssh -L 13001:127.0.0.1:13001 -L 18001:127.0.0.1:18001 user@amp-host
```

Open `http://127.0.0.1:13001/` locally.

## Site dev gate (Season 5 landing)

When `NEXT_PUBLIC_SITE_DEV_GATE=1`, the entire UI is replaced by a dev landing page until the visitor redeems a **character** code and has `tfmc.map.staff` in `permission_flags`.

**Security:** Client-side gate only; API routes remain reachable if endpoints are known. Unset on public launch.

Config detail: [docs/ops/dev-config.md](./docs/ops/dev-config.md)

- [ ] Gate **off**: site works as today (hub, map, skins, etc.)
- [ ] Gate **on**, no session: dev landing on all routes
- [ ] Gate **on**, staff character code: full site visible

## Free-text validation

Display names and prose fields are validated server-side (`backend/src/text_validation.py`; frontend mirror: `frontend/lib/textValidation.ts`). Invalid input is rejected at the API (400).

## Port already in use?

```bash
sudo ss -tlnp | grep -E '18001|13001|8001'
```

Change the left-hand side of `ports:` in `docker-compose.staging.yml` if needed; keep container ports `8000` / `3000`.
