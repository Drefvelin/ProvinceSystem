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

Automated API path: `python scripts/skins_e2e_smoke.py` from `backend/` (link + notify + review; Step 11: IGN-based ids, multi-tier armor, no `player_key`).

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

Bow kinds need four/five multipart fields (`texture`, `pull_0`, `pull_1`, `pull_2`, + `charged` for crossbow) — **filenames are freeform**, the server writes fixed `{id}...` stems itself. Sizes: bow/crossbow 16×16; large_bow 32×32.

1. Deploy latest `Builds/ArmourShop/armourshop-*.jar`. On the **server** `plugins/ArmourShop/config.yml` (do not commit secrets):
   - `skins-api.base-url`: `http://127.0.0.1:18001` (or host-reachable staging API)
   - `skins-api.plugin-key`: same as compose `PLUGIN_KEY` (default `dev-plugin-key`)
   - `pack-apply.ia-contents-path`: absolute path to live ItemsAdder `contents/`
   - `pack-apply.categories-path`: absolute path to ArmourShop `Categories/`
   - `pack-apply.force-reload-time`: `"06:00"` server-local daily force pull + IA refresh (blank disables)
   - `pack-apply.ia-reload-delay-seconds`: seconds between `iareload` and `iazip` (default `5`)
2. Link Discord + mint + redeem (Step 5 / mint section above).
3. On `http://127.0.0.1:13001/skins`: choose kind. Armor: **Add tier** (1–6 of `iron/steel/abyssalite/mythril/mage/infantry`), 6 uploads per tier; non-armor: pick filtered **`base_set`** (no `item`), grip only for `large_handheld`. Upload any PNG file — filenames don't matter, the API derives the id from your linked Minecraft name + item name. Optional **Apply name** adds colours/styles. Site blocks if you already have an active submission with that item name.
4. Staff **Approve** in `#bot-feed` (embed shows the human submission id, Minecraft + Discord names, tiers or base set — never raw UUIDs).
5. Pack apply happens via:
   - **Manual:** `/armourshop pack pull` (force — runs even with players online)
   - **Empty server:** last player quit → auto pull + IA refresh if queue/API pending
   - **Daily:** `force-reload-time` (force)
   Expect console: pack write (**N files per tier for armor**) / shop (**N SkinSets for armor, one per tier, sharing one LP grant**) / LP (API, no `lp` chat) / `iareload` → delay → `iazip` / applied ack.
   Shop YAML uses plain `name` + separate `colour` (string or list) + optional `add-name` / `styles` (TLibs gradient at runtime).
6. Confirm id left the approved list:

```bash
curl -s http://127.0.0.1:18001/skins/plugin/approved \
  -H "X-Plugin-Key: dev-plugin-key"
```

7. Issuer opens ArmourShop → set(s) under **Player Armor** (`ps_armor`, one per tier) or **Player Items** (`ps_items`) → apply onto matching BaseSet/tier gear in inventory.
8. Staff delete (optional): `/armourshop submission delete <human-id>` (tab-completes ids like `drefvelin_blue_knight`, never a UUID) clears **all tiers'** shop + pack files + shared LP node and marks API `revoked`. Delete only **enqueues** the deferred IA refresh — it does not force an immediate `iareload`/`iazip`, even with staff online; the queued reload flushes on the next empty-server tick or the daily force time.

Operator checklist:

- [ ] Redeploy API (migrate drops `player_keys`; ignore any leftover unused column); bot; rebuild ArmourShop (+ TLibs if needed)
- [ ] Config: staging API + live `pack-apply.*` paths (+ force time / IA delay)
- [ ] Submit **multi-tier armor** (e.g. iron + steel) with arbitrary PNG filenames — accepted; id built from IGN + item name
- [ ] Upload blocked when same player reuses the same item name (no separate base-id conflict check)
- [ ] Approve → pack pull writes **N SkinSets** for an N-tier armor submission; `#bot-feed` shows names + tiers, not UUIDs
- [ ] `/armourshop submission delete <human-id>` tab-completes and removes shop/pack for all tiers; status revoked; IA refresh only **queued** (not forced)
- [ ] Issuer sees set(s) and applies onto matching BaseSet/tier gear

Failure modes: players online delays non-force IA refresh; LuckPerms missing so shop hides set; wrong BaseSet/tier gear in inventory; Mojibake `Â` means jar/source encoding still wrong; item name too long combined with IGN (shorten item name — 48-char id cap).

Checkpoint:

```text
approve → pack pull (N tiers) → shop + LP API → iareload → iazip → applied → issuer applies skin
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
