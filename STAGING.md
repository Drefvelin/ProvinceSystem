# Staging stack (AMP host / SSH)

Temporary ProvinceSystem next to production for Discord bot testing. Uses ports **18001** (API) and **13001** (UI). Production `docker-compose.yml` (8000/3000) is unchanged.

(If an older doc said 8001: that port is often already in use on the host.)

Data lives only under this clone (`backend/src/data`, etc.).

## Prerequisites

- Docker + Docker Compose on the host
- Git access to this repo

## Update staging clone (every pull)

Staging boxes should track the remote branch **exactly**. Do **not** keep local edits (including `chmod +x` dirtying the scripts — that makes `git pull` fail with “local changes would be overwritten”).

Use your staging path (`~/ProvinceSystem` or `~/tfmc-staging`). Checkout the branch you run on staging (often `tfmc-bot`). After `reset --hard`, always `chmod +x` again before running scripts.

```bash
cd ~/ProvinceSystem
git fetch origin
git checkout tfmc-bot
git reset --hard origin/tfmc-bot
chmod +x scripts/staging-*.sh
```

`reset --hard` discards any local chmod/script tweaks so the tree matches GitHub. Then set execute bits again before running the scripts.

## Start (SSH)

First-time clone:

```bash
git clone <ProvinceSystem-git-url> ~/tfmc-staging
cd ~/tfmc-staging
git checkout tfmc-bot
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

## Red bot (`skinsreview` config.yml)

On the same machine as AMP/Red:

```yaml
api_base_url: "http://127.0.0.1:18001"
staff_key: "dev-staff-key"
bot_feed_channel_id: YOUR_BOT_FEED_CHANNEL_ID
poll_interval_seconds: 60
```

Then in Discord: `-reload skinsreview` → `/skinsreview ping`.  
Enable slash if needed: `!slash enable skinsreview` then `!slash sync`.

## Step 5 — Discord link + player DMs (manual)

Automated API path: `python scripts/skins_e2e_smoke.py` from `backend/` (link + notify + review).

Live Discord path (operator):

1. **Link** — In game `/linkdiscord` (ArmourShop `skins-api` → staging URL + plugin key), **or** curl:

```bash
curl -s -X POST http://127.0.0.1:18001/skins/discord/link/start \
  -H "Content-Type: application/json" \
  -H "X-Plugin-Key: dev-plugin-key" \
  -d '{"player_uuid":"00000000-0000-0000-0000-000000000001","minecraft_name":"Test"}'
```

2. In TFMC Discord: `/linkdiscord code:<CODE>` (ephemeral success).
3. Mint via `/armourshop token create` (or curl below) → redeem + upload on `http://127.0.0.1:13001/skins`.
4. Confirm **submitted** DM; submission appears in `#bot-feed`.
5. Approve or Deny → **outcome** DM (+ reason if denied).
6. Confirm API/status shows `player_uuid` + linked Discord (staff embed / pending).

**Unlink (wrong account / alt):**

- In game on the **linked** UUID: `/unlinkdiscord`
- Or in Discord (any MC): `/unlinkdiscord` — clears by Discord user id (fixes “Discord stuck on alt”)
- Then `/linkdiscord` again on the correct account
- Guards already in place: one Discord ↔ one UUID; each skins code redeems **once**

Checkpoint:

```text
link → redeem + upload → submitted DM → Approve/Deny → outcome DM
```

## Mint a code + submit a skin

**Preferred (in-game, Step 6):**

1. Deploy `Builds/ArmourShop/armourshop-1.1.2.jar` with `skins-api.base-url` / `plugin-key` pointing at staging.
2. Grant LP `armourshop.token.create` (or use `armourshop.admin`).
3. Optional first: `/linkdiscord` → Discord complete (required before **upload**, not for mint).
4. `/armourshop token create` → click the aqua code to copy (tab: `token` → `create`).
5. Open `http://127.0.0.1:13001/skins`, redeem, upload → `#bot-feed` / DMs as Step 5.

Operator checklist:

- [ ] Discord linked for test UUID (Step 5)
- [ ] LP: `armourshop.token.create` (or admin)
- [ ] `/armourshop token create` → click-copy
- [ ] Redeem + upload on staging UI
- [ ] `#bot-feed` / submitted + outcome DMs

**API-only fallback** (curl against staging):

```bash
curl -s -X POST http://127.0.0.1:18001/skins/codes \
  -H "Content-Type: application/json" \
  -H "X-Plugin-Key: dev-plugin-key" \
  -d '{"player_uuid":"00000000-0000-0000-0000-000000000001"}'
```

**Browser UI from your PC** (tunnel both ports):

```bash
ssh -L 13001:127.0.0.1:13001 -L 18001:127.0.0.1:18001 user@amp-host
```

Open `http://127.0.0.1:13001/skins`, redeem the code, upload (**Discord must already be linked** for that UUID), wait for `#bot-feed` (or `/skinsreview post <id>`).

## Keys (compose defaults)

| Env | Value |
|-----|--------|
| `SKINS_DEV` | `1` |
| `STAFF_KEY` | `dev-staff-key` |
| `PLUGIN_KEY` | `dev-plugin-key` |

Override in `docker-compose.staging.yml` if you want stronger keys for a longer-lived staging box.

## Port already in use?

```bash
sudo ss -tlnp | grep -E '18001|13001|8001'
```

Change the left-hand side of `ports:` in `docker-compose.staging.yml` if needed, keep container ports `8000` / `3000`.
