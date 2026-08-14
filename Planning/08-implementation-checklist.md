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

- [x] Banned role id in config
- [x] Add role on ban notify ([step-17.07](./batches/step-17/07-warn-and-ban-mirror.md))
- [x] Unban/clear removes role
- [ ] Channel overwrites documented for staff

**Done when:** Flow 3 role mute works; MC bans still in-game only.

---

## Track — Map platform ([16-map-platform.md](./16-map-platform.md))

**Repos:** `ProvinceSystem` · `Workspace/simplefactions` · TFMCWeb (staff map gate)

### M0 — Planning lock

- [x] [step-36](./batches/step-36/00-index.md) — Playbook + export schema + hub docs

### M1 — Site UX and interaction ([step-37](./batches/step-37/00-index.md))

**Step 37 done (37.01–37.06).**

- [x] Split `MapViewer`; site styling parity ([37.02](./batches/step-37/02-split-map-viewer.md))
- [x] Cropped overlays + bbox metadata
- [x] Click nation modal; Ctrl+click drill
- [x] Mobile layout
- [x] Hover perf (rAF, RGB→id map); wire realm size/subjects

### M2 — Parchment visual pipeline ([step-38](./batches/step-38/00-index.md)) — **done**

- [x] [38.01](./batches/step-38/01-planning-lock.md) planning lock
- [x] [38.02](./batches/step-38/02-parchment-base.md) `map.png` → parchment base + `/map` serve
- [x] [38.03](./batches/step-38/03-muted-political.md) desaturated region overlays + borders
- [x] [38.04](./batches/step-38/04-frontend-composite.md) frontend layer tuning
- [x] [38.05](./batches/step-38/05-docs-verify.md) docs + STAGING

### M2b — Ink cartography ([step-39](./batches/step-39/00-index.md)) — **done**

- [x] [39.01](./batches/step-39/01-planning-lock.md) planning lock
- [x] [39.02](./batches/step-39/02-ink-base.md) luminance remap + ink edge overlay
- [x] [39.03](./batches/step-39/03-earth-tone-fills.md) faithful-hue parchment washes
- [x] [39.04](./batches/step-39/04-adaptive-borders.md) uniform INK_DARK borders
- [x] [39.05](./batches/step-39/05-frontend-opacity.md) hover vs drill opacity split
- [x] [39.06](./batches/step-39/06-docs-verify.md) docs + STAGING

### M3 — Labels ([step-40](./batches/step-40/00-index.md)) — **done**

- [x] [40.02](./batches/step-40/02-map-geometry.md) province neighbors + centroids JSON for `main`
- [x] [40.03](./batches/step-40/03-layout-lib.md) `computeNationLabels()` + unit tests
- [x] [40.04](./batches/step-40/04-frontend-layer.md) `LabelLayer` in `MapCanvas`; nation mode only
- [x] [40.05](./batches/step-40/05-label-polish.md) ink + halo styling; zoom-hide stub
- [x] [40.06](./batches/step-40/06-docs-verify.md) docs + STAGING

### M4 — Access ([step-41](./batches/step-41/00-index.md)) — **next**

- [ ] Staff-only maps (configurable per `mapId`)

### M5 — Settlements ([step-42](./batches/step-42/00-index.md))

- [ ] SF named capitals / guild settlements export + map markers

### M6 — Forts ([step-43](./batches/step-43/00-index.md))

- [ ] Forts + zone of control (SF forts required)

### M7 — Wars ([step-44](./batches/step-44/00-index.md))

- [ ] War frontlines layer (**blocked on SF war rework**)

### M8 — Chronicle ([step-45](./batches/step-45/00-index.md))

- [ ] Daily snapshots + event changelog

### M9 — Wealth analytics ([step-46](./batches/step-46/00-index.md))

- [ ] Nation / global wealth time series + charts

### M10 — SimpleFactions hygiene (when touching plugin)

**Repo:** `Workspace/simplefactions`

- [ ] Move API URL + regen secret to config (stop hardcoding hash in source)
- [ ] Confirm `mapRef` matches website `mapId` per world

**Done when:** [16-map-platform.md](./16-map-platform.md) success criteria met.

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
10. **Character creator / Step 19 Phase 1** — **done** (19.01–19.06); staging verified  
11. **Starter kits / Step 20** — plumbing **done** (20.01–20.03); claim [21.06](./batches/step-21/06-kit-claim-command.md); multi-kit [21.08](./batches/step-21/08-kits-yml-and-kit-service.md)  
12. **Kits + lore customise / Step 21** — **done** ([step-21](./batches/step-21/00-index.md); 21.07 superseded)  
13. **Web character sheet / Step 22** — **done** ([step-22](./batches/step-22/00-index.md); [22.03](./batches/step-22/03-docs-verify.md))  
14. **Kit lore editor polish / Step 23** — **done** ([step-23](./batches/step-23/00-index.md); [23.04](./batches/step-23/04-docs-verify.md))  
15. **Character sheet parity / Step 24** — **done** ([step-24](./batches/step-24/00-index.md); [24.04](./batches/step-24/04-docs-verify.md))  
16. **Kit submit + deny UX / Step 25** — **done** ([step-25](./batches/step-25/00-index.md); [25.03](./batches/step-25/03-docs-verify.md))  
17. **Kit asset sync + status / Step 26** — **done** ([step-26](./batches/step-26/00-index.md); [26.03](./batches/step-26/03-docs-verify.md))  
18. **Kit templates + resetkit / Step 27** — **done** ([step-27](./batches/step-27/00-index.md); [27.05](./batches/step-27/05-docs-verify.md))  
19. **Book skins + kit journal / Step 28** — **done** ([step-28](./batches/step-28/00-index.md); 28.07 docs closed)  
20. **Kit customise visibility + claim AS gate / Step 29** — **done** ([step-29](./batches/step-29/00-index.md); 29.06 docs closed)  
21. **Character skin wardrobe / Step 30** — **done** ([step-30](./batches/step-30/00-index.md); 30.08 docs closed)  
22. **Drink Builder / Step 31** — **done** ([15](./15-drink-builder.md) / [step-31](./batches/step-31/00-index.md); 31.09 docs closed)  
23. **Realm + TFMCWeb gateway / Steps 32–35** — **done** (code; staging [STAGING](../STAGING.md) Steps 32–35)  
24. **Map platform planning lock / Step 36** — **done** ([16-map-platform.md](./16-map-platform.md))  
25. **Map site UX / Step 37** — **done** ([step-37](./batches/step-37/00-index.md))  
26. **Map parchment pipeline / Step 38** — **done** ([step-38](./batches/step-38/00-index.md); tick [STAGING](../STAGING.md) Step 38 when ready)  
27. **Ink cartography / Step 39** — **done** ([step-39](./batches/step-39/00-index.md); tick [STAGING](../STAGING.md) Step 39 when ready)  
28. **Nation labels / Step 40** — **done** ([step-40](./batches/step-40/00-index.md); tick [STAGING](../STAGING.md) Step 40 when ready)  
29. **Staff maps / Step 41** — **next build**  
30. **Settlements, forts, wars, chronicle, wealth / Steps 42–46**  
31. Tick [STAGING](../STAGING.md) Steps 17–35, 31 when ready  
32. **SimpleFactions via TFMCWeb / Step 47** — later (post map platform)  

---

## Definition of “finished product” (platform MVP)

| Area | Criteria |
|------|----------|
| Map | Ink political map; nation modals; staff map gates; settlements; daily chronicle + wealth charts ([16](./16-map-platform.md) / steps 37–46) |
| Skins | armor_set + item/handheld/large_handheld; exact sizes; naming; Discord PNG review; ArmourShop pack + LP |
| Drinks | Token → `/drinks` → Discord → DrinkBuilder → BreweryX + optional `tfmc_drinks` (**code done**; staging [STAGING](../STAGING.md) Step 31) |
| Bot | Skins + drinks review; ban DM/log + **banned role add/clear done**; guild leave/join grace |
| TFMCWeb | Survival Discord gate; `/token create skin|drink`; shared mint cooldown; ArmourShop no longer owns link |
| Ops | Local website demo without Paper; deferred IA reload when safe |

Post-MVP later: Discord multi-view 3D review bake (after [step-16](./batches/step-16/00-index.md) site viewer), SimpleFactions via TFMCWeb ([step-46](./batches/README.md)).  
Steps 17–35 **done** (code). Step 36 map platform planning lock **done**. **Step 37 code done (37.01–37.06).** **Step 38 parchment pipeline done (38.01–38.05).** **Step 39 ink cartography done (39.01–39.06).** **Step 40 nation labels done (40.01–40.06).** Next build: [step-41 staff map access](./batches/step-41/00-index.md). Steps 42–46 **planned** ([16-map-platform.md](./16-map-platform.md)). Tick operator [STAGING](../STAGING.md) Steps 37–40 when ready.
