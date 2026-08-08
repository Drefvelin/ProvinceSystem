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

2. In TFMC Discord: `/linkdiscord code:<CODE>` (ephemeral success). In game, ArmourShop polls notices (~1s) and chats link success if the player is online.
3. Mint via `/armourshop token create` (or curl below) → redeem + upload on `http://127.0.0.1:13001/skins`.
4. Confirm **submitted** DM; submission appears in `#bot-feed`.
5. Approve or Deny → **outcome** DM (+ reason if denied).
6. Confirm API/status shows `player_uuid` + linked Discord (staff embed / pending).

If already linked, in-game `/linkdiscord` does **not** mint a new code — it says already linked (with Discord name when stored). Use `/unlinkdiscord` first to relink.

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
3. `/linkdiscord` → Discord complete (**required before mint**).
4. `/armourshop token create` → click the aqua code to copy (tab: `token` → `create`).
5. Open `http://127.0.0.1:13001/skins`, redeem, upload → `#bot-feed` / DMs as Step 5.

Admin: `/armourshop listtokens` lists unused unexpired codes (issuer + red `[Delete]` → `/armourshop token delete <code>`).

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

## Step 8 — Flow 2 apply (armor / melee)

End-to-end for kinds with pack writers: **`armor_set`**, **`handheld`**, **`large_handheld`**, **`bow`**, **`large_bow`**, **`crossbow`**.

Bow kinds need multi-frame PNGs with the **same id prefix**: `{id}.png` + `{id}_0.png` / `_1` / `_2` (crossbow also `{id}_charged.png`). Sizes: bow/crossbow 16×16; large_bow 32×32.

1. Deploy latest `Builds/ArmourShop/armourshop-*.jar`. On the **server** `plugins/ArmourShop/config.yml` (do not commit secrets):
   - `skins-api.base-url`: `http://127.0.0.1:18001` (or host-reachable staging API)
   - `skins-api.plugin-key`: same as compose `PLUGIN_KEY` (default `dev-plugin-key`)
   - `pack-apply.ia-contents-path`: absolute path to live ItemsAdder `contents/`
   - `pack-apply.categories-path`: absolute path to ArmourShop `Categories/`
2. Link Discord + mint + redeem (Step 5 / mint section above).
3. On `http://127.0.0.1:13001/skins`: choose kind + filtered **`base_set`** (no `item`); grip only for `large_handheld`; upload PNGs named per Planning naming docs.
4. Staff **Approve** in `#bot-feed` (outcome DM).
5. In game (admin): `/armourshop pack pull` — expect `wrote` / shop / lp / `queued=N`.
6. Deferred IA reload: when server is **empty**, or on **restart**, ArmourShop runs console **`iazip`**, then `POST /skins/plugin/applied`. Confirm id left the approved list:

```bash
curl -s http://127.0.0.1:18001/skins/plugin/approved \
  -H "X-Plugin-Key: dev-plugin-key"
```

7. Issuer opens ArmourShop → set under **Player Armor** (`ps_armor`) or **Player Items** (`ps_items`) → apply onto matching BaseSet gear in inventory.

Operator checklist:

- [ ] Config: staging API + live `pack-apply.*` paths
- [ ] Upload armor or handheld/large with kind + `base_set`
- [ ] Approve → `/armourshop pack pull` wrote + queued
- [ ] Empty server or restart → `iazip` → applied ack (id gone from approved)
- [ ] Issuer sees set and applies onto matching BaseSet gear

Failure modes: players online delays `iazip`; LuckPerms missing so shop hides set; wrong BaseSet gear in inventory; bow frame names must share the same `{id}` prefix.

Checkpoint:

```text
approve → pack pull → shop + LP → iazip → applied → issuer applies skin
```

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
