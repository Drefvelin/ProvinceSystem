# Staging stack (AMP host / SSH)

Temporary ProvinceSystem next to production for Discord bot testing. Uses ports **18001** (API) and **13001** (UI). Production `docker-compose.yml` (8000/3000) is unchanged.

(If an older doc said 8001: that port is often already in use on the host.)

Data lives only under this clone (`backend/src/data`, etc.).

## Prerequisites

- Docker + Docker Compose on the host
- Git access to this repo

## Update staging clone (every pull)

Staging boxes should track the remote branch **exactly**. Do **not** keep local edits (including `chmod +x` dirtying the scripts — that makes `git pull` fail with “local changes would be overwritten”).

Use your staging path (`~/ProvinceSystem` or `~/tfmc-staging`). Checkout the branch you run on staging (**`site-rework`**). After `reset --hard`, always `chmod +x` again before running scripts.

```bash
cd ~/ProvinceSystem
git fetch origin
git checkout site-rework
git reset --hard origin/site-rework
chmod +x scripts/staging-*.sh
```

`reset --hard` discards any local chmod/script tweaks so the tree matches GitHub. Then set execute bits again before running the scripts.

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

## Step 17 — TFMCWeb identity + Discord gate (current)

**Playbook:** [Planning/13-tfmcweb.md](./Planning/13-tfmcweb.md) · full checklist [Planning/batches/step-17/08-docs-verify.md](./Planning/batches/step-17/08-docs-verify.md).

### Deploy

1. ProvinceSystem API on staging (identity grace + moderation outbox).
2. `Builds/TFMCWeb/tfmcweb-*.jar` with `plugins/TFMCWeb/config.yml`:
   - `api.base-url`: `http://127.0.0.1:18001`
   - `api.plugin-key`: same as API `PLUGIN_API_KEY`
3. ArmourShop cutover jar (pack apply only; `skins-api` still for approved packs).
4. RPCharacters with Discord gate freeze API.
5. Bot: skinsreview `guild_id` + leave/join; minecraftban `config.yml` (`api_base_url`, `staff_key`, `banned_role_id` — role id required for role checks).
6. LuckPerms: `tfmcweb.token.create` (migrate from `armourshop.token.create`); staff `tfmcweb.warning`.

### Link + mint (operator)

1. Survival: `/linkdiscord` (TFMCWeb) → Discord `/linkdiscord code:<CODE>` → notices via TFMCWeb poller.
2. `/token create skin` → click-copy → redeem + upload on `http://127.0.0.1:13001/skins`.
3. Approve/Deny in `#bot-feed` → outcome DMs (skinsreview).
4. Optional: `/token create character` (redeem stub 501 until character creator).
5. `/armourshop token create` redirects to `/token create skin` (obsolete AS mint).

If already linked, `/linkdiscord` does not mint a new code. Use `/unlinkdiscord` (in-game or Discord) to relink. One Discord ↔ one UUID.

### Gate / grace / moderation smoke

- Survival unlinked → frozen; message points to `/linkdiscord`. Non-Survival staff not gated.
- Leave guild → ≤1h play; rejoin clears; after expire → freeze.
- `/warning` + `/tempban` (or CE `/tfmc ban`) → Discord DM + Banned role; `/unban` clears role.

Checkpoint: see [08-docs-verify.md](./Planning/batches/step-17/08-docs-verify.md).

## Step 18 — Staff curated skins

**Playbook:** [Planning/batches/step-18/00-index.md](./Planning/batches/step-18/00-index.md) · checklist [Planning/batches/step-18/06-docs-verify.md](./Planning/batches/step-18/06-docs-verify.md).

**Code:** 18.01–18.06 done (API catalog + staff codes, TFMCWeb mint, ArmourShop `tfmc_armorshop` apply, web dropdowns). Tick boxes below on live staging.

### Deploy

1. Latest ProvinceSystem API (staff submit + catalog store).
2. `Builds/ArmourShop/armourshop-*.jar` — catalog sync + staff pack/shop path.
3. `Builds/TFMCWeb/tfmcweb-*.jar` — `/token create skin staff`.
4. Frontend with staff category/scroll UI on `/skins`.
5. ArmourShop `config.yml`: `scrolls:` list (`id` + `label`); `skins-api` + `pack-apply.*` as for Step 8.
6. ItemsAdder: `contents/tfmc_armorshop/` scaffold present (beside `tfmc_submissions`).
7. LuckPerms: grant **`tfmcweb.token.create.staff`** to staff who mint curated codes (does not require `tfmcweb.token.create`).

### Operator checklist

- [ ] Scrolls listed in AS `config.yml`; enable (or `/armourshop catalog sync`) syncs catalog — `GET /skins/catalog` shows categories + scrolls
- [ ] `/token create skin staff` → redeem on `/skins` → category + scroll dropdowns visible
- [ ] Staff armor → pack under `tfmc_armorshop` + chosen `a_*` category YAML with scroll; usable in shop via scroll
- [ ] Staff gun → IA + GaG `skins.yml` + item category entry
- [ ] Player `/token create skin` → still Discord review + `tfmc_submissions` / `ps_*` + LP
- [ ] No bot / `#bot-feed` post for staff submit

Checkpoint:

```text
catalog sync → /token create skin staff → redeem + dropdowns → auto-approve
  → pack pull → tfmc_armorshop + category/scroll → shop usable
```

## Step 5 — Discord link + player DMs (historical)

> **Obsolete path notes:** Step 5 used ArmourShop for `/linkdiscord` and `/armourshop token create`. **Current owner is TFMCWeb** (Step 17). Curl snippets below remain for API smoke without the plugin.

Automated API path: `python scripts/skins_e2e_smoke.py` from `backend/` (link + notify + review).

```bash
curl -s -X POST http://127.0.0.1:18001/skins/discord/link/start \
  -H "Content-Type: application/json" \
  -H "X-Plugin-Key: dev-plugin-key" \
  -d '{"player_uuid":"00000000-0000-0000-0000-000000000001","minecraft_name":"Test"}'
```

Live path today: TFMCWeb `/linkdiscord` → Discord complete → `/token create skin` → site redeem (see Step 17).

## Mint a code + submit a skin

**Preferred (in-game, TFMCWeb / Step 17):**

1. Deploy `Builds/TFMCWeb/tfmcweb-*.jar` with `api.base-url` / `api.plugin-key` pointing at staging.
2. Grant LP `tfmcweb.token.create` (or use `tfmcweb.admin`).
3. `/linkdiscord` → Discord complete (**required before mint**).
4. `/token create skin` → click the aqua code to copy.
5. Open `http://127.0.0.1:13001/skins`, redeem, upload → `#bot-feed` / DMs as Step 5 (historical DM flow).

Admin: `/armourshop listtokens` lists unused unexpired codes (issuer + red `[Delete]` → `/armourshop token delete <code>`).

Operator checklist:

- [ ] Discord linked for test UUID (TFMCWeb / Step 17)
- [ ] LP: `tfmcweb.token.create` (or admin)
- [ ] `/token create skin` → click-copy
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

Open `http://127.0.0.1:13001/skins`, redeem the code, upload (**Discord must already be linked** for that UUID). The site shows **Submitting…** until the composite review sheet is built, then the status page displays that sheet. Wait for `#bot-feed` (or `/skinsreview post <id>`) — Discord gets the same `review_sheet.png`, not raw 16×16 files.

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
2. Link Discord + mint + redeem (Step 17 / mint section above).
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
