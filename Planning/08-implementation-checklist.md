# 08 — Implementation checklist (full platform)

Cross-repo build order for map, skins, bot, and pack. Journeys: [12-end-to-end-flows.md](./12-end-to-end-flows.md). Roadmap tracks: [03-roadmap.md](./03-roadmap.md).

Repos: `ProvinceSystem` (`dev`) | `tfmc_bot` | `Workspace/armourshop` | `Workspace/simplefactions` | ItemsAdder contents.

---

## Sprint 0 — Docs

- [x] Platform Planning playbook (README + 01–13; TFMCWeb in [13](./13-tfmcweb.md) / [step-17](./batches/step-17/00-index.md))

---

## Track — Pack scaffold (anytime before ArmourShop apply)

**Repo / server:** ItemsAdder (`Workspace/plugins/ItemsAdder` + keep `ItemsAdder Copy` in sync for reference)

- [ ] Create empty namespace **`tfmc_submissions`** (configs + resourcepack folders)
- [ ] Deploy scaffold to live so ArmourShop only appends files later
- [ ] Document path in ArmourShop config ([10](./10-armourshop-itemsadder.md))

---

## Track — Skins (ProvinceSystem → bot → ArmourShop)

### S1 — API foundation

**Repo:** `ProvinceSystem`

- [x] SQLite + migrations (`codes`, `submissions`)
- [x] `data/skins/` + compose volume + gitignore
- [x] Slug validation ([07](./07-naming-conventions.md))
- [x] Routes: issue, redeem, upload armor_set/item/handheld/large_handheld, status, staff approve/deny, review-sheet
- [x] Exact PNG sizes + `grip_preset` for large_handheld
- [x] Seed mock code; env `PLUGIN_KEY` / `STAFF_KEY`

**Done when:** curl armor_set (correct sizes) stores six fixed stems; large_handheld+grip works; approve works; review-sheet returns PNG.  
**Verified:** `backend/scripts/skins_e2e_smoke.ps1` (Step 2.08).

### S2 — Website `/skins`

**Repo:** `ProvinceSystem` frontend

- [x] Shell nav + redeem + kind forms (6 armor slots / item kinds + grip) + status + slug UX

**Done when:** Browser path works without Discord/ArmourShop.  
**Verified:** Step 3 batches 3.01–3.04 (`/`, `/map/main`, `/skins`, `/skins/[id]`).

### S3 — Discord skins cog

**Repo:** `tfmc_bot` (Red on AMP) — [11](./11-discord-bot.md) · [batches/step-4](./batches/step-4/00-index.md)

- [x] Staff API: pending list + staff file download
- [x] Cog: `#bot-feed` embed + **raw PNG** attachments + Approve/Deny + message update
- [x] Poll (or slash) intake without duplicate posts

**Done when:** Staff can review staging/local submissions in Discord from raw files (review-sheet attach later).

**Verified:** Step 4 batches 4.01–4.05 implemented; AMP E2E against local/staging API is the runtime check.

### S3.5 — Discord link + player DMs

**Repos:** ProvinceSystem + `tfmc_bot` + TFMCWeb `/linkdiscord` (historically ArmourShop) — [batches/step-5](./batches/step-5/00-index.md) · [step-17](./batches/step-17/00-index.md)

- [x] Link API: start (plugin) + complete (staff) + `discord_links`
- [x] Submit requires link; stamp `discord_user_id`; submitted notification outbox
- [x] Cog: `/linkdiscord`; DMs for submitted / approved / denied
- [x] `/linkdiscord` → `link/start` (now TFMCWeb; was ArmourShop)
- [x] Smoke green (`skins_e2e_smoke.py` — link + notify + review)
- [ ] Live Discord DM path on staging/AMP — operator checklist in [STAGING.md](../STAGING.md)

**Done when:** Player links once, uploads without typing Discord/MC ids, and receives the three DMs (live path verified on staging).

### S3.6 — In-game skins token

**Repo:** `Workspace/armourshop` — [batches/step-6](./batches/step-6/00-index.md)

- [x] Click-to-copy chat helper; `POST /skins/codes` client; `/linkdiscord` uses copy
- [x] `/token create skin` (TFMCWeb; perm `tfmcweb.token.create`); AS mint redirects
- [ ] Staging: mint → redeem on site → upload

**Done when:** Donator (LP) mints in game, clicks to copy, redeems on `/skins` without curl.

### S4a — Pack writer (dry-run)

**Repo:** `Workspace/armourshop` — [batches/step-7](./batches/step-7/00-index.md)

- [x] Scaffold empty `tfmc_submissions`; document IA contents path config
- [x] Writer: `armor_set` (`generate: true` + `armors_rendering`)
- [x] Writer: `item` / `handheld` (`generate: true` + parent)
- [x] Grip templates + `large_handheld` (`generate: false` + thin models)
- [x] Fixture harness writes all four kinds to an out dir

**Done when:** Harness produces valid pack files without Discord/live poll.

### S4b — Plugin apply (live)

**Repo:** ProvinceSystem + `Workspace/armourshop` — [batches/step-8](./batches/step-8/00-index.md) · [10](./10-armourshop-itemsadder.md)

- [x] API: `base_set` + kind allowlists / pairing; reject `item` ([8.01](./batches/step-8/01-base-set-api.md))
- [x] UI: enabled kinds; filtered tier/type dropdowns; no `item` ([8.02](./batches/step-8/02-base-set-ui.md))
- [x] Pull `GET /plugin/approved` + pack write for armor/handheld/large ([8.03](./batches/step-8/03-pull-and-write.md))
- [x] Shop `ps_armor` / `ps_items` + LP `armourshop.submission.{slug}`; merge `item-start-points` ([8.04](./batches/step-8/04-shop-and-lp.md))
- [x] Deferred IA reload + `POST /plugin/applied` ([8.05](./batches/step-8/05-reload-and-ack.md))
- [ ] Staging E2E armor/melee Flow 2 ([8.06](./batches/step-8/06-docs-e2e.md))
- [x] Bow / large_bow / crossbow writers + harness + apply ([8.07](./batches/step-8/07-bow-crossbow-writers.md))
- [x] Name colour / encoding / website Apply name ([step-9](./batches/step-9/00-index.md))
- [x] Player key prefix, collision check, staff delete, bot names ([step-10](./batches/step-10/00-index.md))
- [x] IGN-based human ids (no `player_key`), ignore upload filenames, multi-tier armor (1–6), deferred-only delete ([step-11](./batches/step-11/00-index.md))

**Done when:** Flow 2 complete for melee/armor in [12](./12-end-to-end-flows.md); bow kinds after 8.07.

### S5 — Item 3D + shield + helmet 3D ([step-13](./batches/step-13/00-index.md))

- [x] `item_3d` / `shield` / `helmet_3d` API/UI + display autofill + ArmourShop apply (shield blocking auto; armor per-tier 3D helmet)
- [x] Guns carry/reload/aim ([step-14](./batches/step-14/00-index.md))
- [x] GaG resolve IA ids instead of CMD ([step-15](./batches/step-15/00-index.md))
- [ ] Upload 3D model preview on `/skins` ([step-16](./batches/step-16/00-index.md)) — start with [16.02 json render](./batches/step-16/02-json-model-render.md)
- [ ] Multi-view review bake for Discord (**later**, after site viewer)
- [ ] Quotas, retention, reserved slugs, tier size caps (**later**)

---

## Track — Bot moderation (parallel with S3)

**Repo:** `tfmc_bot` — [11](./11-discord-bot.md)

- [ ] Banned role id in config
- [ ] Add role on ban notify
- [ ] Unban/clear command removes role
- [ ] Channel overwrites documented for staff

**Done when:** Flow 3 role mute works; MC bans still in-game only.

---

## Track — Map

### M1 — Website map UX

**Repo:** `ProvinceSystem` — [09](./09-map-system.md), [04](./04-map-performance.md)

- [ ] Realm size on hover card
- [ ] Cropped overlays + bbox
- [ ] Hover throttle / RGB map
- [ ] Mobile layout
- [ ] Hub shell (shared with skins)

### M2 — SimpleFactions hygiene (when touching plugin)

**Repo:** `Workspace/simplefactions`

- [ ] Move API URL + regen secret to config (stop hardcoding hash in source)
- [ ] Confirm `mapRef` matches website `mapId` per world
- [ ] No skins logic added here

**Done when:** Flow 1 reliable; map feels fast enough for MVP.

---

## Suggested PR / work sequence

1. Pack scaffold `tfmc_submissions`  
2. ProvinceSystem skins API (S1)  
3. `/skins` UI (S2)  
4. Discord skins cog (S3)  
5. ArmourShop apply (S4)  
6. Map hover card fix (M1 quick win) — parallel anytime  
7. Ban role (bot moderation) — parallel with S3+  
8. **TFMCWeb / Step 17** — done (docs + staging checklist); tick [08-docs-verify](./batches/step-17/08-docs-verify.md) on live staging ([13](./13-tfmcweb.md))  
9. **Staff curated skins / Step 18** — **done** (18.01–18.07); tick staging [06-docs-verify](./batches/step-18/06-docs-verify.md) / [STAGING.md](../STAGING.md)  
10. **Character creator / Step 19 Phase 1** — **done** (19.01–19.06); tick staging [06-docs-verify](./batches/step-19/06-docs-verify.md) / [STAGING.md](../STAGING.md)  
11. Cropped overlays / Phases 2–4 (kit, lore knife, character skins) as capacity allows  

---

## Definition of “finished product” (platform MVP)

| Area | Criteria |
|------|----------|
| Map | Live SF → API → web works; realm card shows size; usable on phone |
| Skins | armor_set + item/handheld/large_handheld; exact sizes; naming; Discord PNG review; ArmourShop pack + LP |
| Bot | Skins review with sheets; ban DM/log + banned role add/clear; guild leave/join grace |
| TFMCWeb | Survival Discord gate; `/token create skin`; ArmourShop no longer owns link |
| Ops | Local website demo without Paper; deferred IA reload when safe |

Post-MVP later: Discord multi-view 3D review bake (after [step-16](./batches/step-16/00-index.md) site viewer), full map overlay crop, brewery module, SF via TFMCWeb.  
Step 13–15 implemented — staging smoke in batch docs. Step 16 planned. Step 17 **17.01–17.08 done**. Step 18 **18.01–18.07 done**. Step 19 character creator Phase 1 **19.01–19.06 done** ([14](./14-character-creator.md) / [step-19](./batches/step-19/00-index.md)); tick staging. Phases 2–4 (kit, lore knife, character skins) after Phase 1 staging green.
