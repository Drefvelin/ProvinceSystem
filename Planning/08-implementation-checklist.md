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

### M3b — Map mode labels ([step-47](./batches/step-47/00-index.md)) — **done**

- [x] [47.01](./batches/step-47/01-planning-lock.md) planning lock
- [x] [47.02](./batches/step-47/02-calavorn-terrain-fertility.md) Calavorn terrain + fertility maps + toolbar
- [x] [47.03](./batches/step-47/03-calavorn-trade-data.md) spoof trade data + regen for `main`
- [x] [47.04](./batches/step-47/04-title-province-rollup.md) `resolveTitleProvinces()` (frontend rollup)
- [x] [47.05](./batches/step-47/05-title-labels-frontend.md) title mode labels on `/map/main`
- [x] [47.06](./batches/step-47/06-trade-labels.md) trade guild labels
- [x] [47.07](./batches/step-47/07-docs-verify.md) docs + STAGING

### M3c — Label neighbor graph ([step-48](./batches/step-48/00-index.md)) — **done**

- [x] [48.01](./batches/step-48/01-planning-lock.md) planning lock
- [x] [48.02](./batches/step-48/02-label-neighbor-geometry.md) `province_label_neighbors.json` builder + `main`/`dev`
- [x] [48.03](./batches/step-48/03-frontend-wiring.md) fetch + `connectedComponents` wiring + tests
- [x] [48.04](./batches/step-48/04-docs-verify.md) docs + STAGING

### M3e — Map title editor ([step-72](./batches/step-72/00-index.md))

- [x] [72.01](./batches/step-72/01-planning-lock.md) planning lock
- [x] [72.02](./batches/step-72/02-staff-write-api.md) staff write API + gate upload
- [x] [72.03](./batches/step-72/03-title-rgb-picker.md) `TitleRgbPicker` + `titleRgb.ts`
- [x] [72.04](./batches/step-72/04-editor-route-shell.md) `/map/editor` route + shell
- [x] [72.05](./batches/step-72/05-province-pick-layer.md) pick canvas + live paint layers
- [x] [72.06](./batches/step-72/06-county-mode.md) county create/edit/delete
- [x] [72.07](./batches/step-72/07-duchy-mode.md) duchy mode
- [x] [72.08](./batches/step-72/08-kingdom-empire-mode.md) kingdom + empire modes
- [x] [72.09](./batches/step-72/09-save-upload-regen.md) save, upload, regen preview
- [x] [72.10](./batches/step-72/10-main-calavorn-prep.md) Calavorn wipe duchy+ runbook
- [x] [72.11](./batches/step-72/11-docs-verify.md) STAGING + QA

Step 72 map title editor **complete** (72.01–72.11).

### M3f — Map editor polish ([step-73](./batches/step-73/00-index.md))

- [x] [73.01](./batches/step-73/01-planning-lock.md) UX lock (nav, entry, locked map)
- [x] [73.02](./batches/step-73/02-nav-and-entry.md) nav cleanup + viewer Edit titles
- [x] [73.03](./batches/step-73/03-locked-map-editor.md) remove map selector; require `?map=`
- [x] [73.04](./batches/step-73/04-layout-overflow.md) flex overflow / layout fix
- [x] [73.05](./batches/step-73/05-province-index-perf.md) province index build perf
- [x] [73.06](./batches/step-73/06-canvas-paint-perf.md) incremental canvas paint
- [x] [73.07](./batches/step-73/07-docs-verify.md) STAGING + hub docs

Step 73 map editor polish **complete** (73.01–73.07).

### M3g — Editor offline export ([step-74](./batches/step-74/00-index.md))

- [x] [74.01](./batches/step-74/01-planning-lock.md) offline export lock
- [x] [74.02](./batches/step-74/02-precomputed-grid-only.md) precomputed grid only
- [x] [74.03](./batches/step-74/03-loading-progress.md) loading progress UI
- [x] [74.04](./batches/step-74/04-export-zip.md) download ZIP (no save to server)
- [ ] [74.05](./batches/step-74/05-reset-and-toolbar.md) reset + toolbar cleanup
- [ ] [74.06](./batches/step-74/06-api-deprecation.md) API deprecation
- [ ] [74.07](./batches/step-74/07-docs-verify.md) STAGING + hub docs

### M3d — Pan and zoom ([step-49](./batches/step-49/00-index.md)) — **done**

- [x] [49.01](./batches/step-49/01-planning-lock.md) planning lock
- [x] [49.02](./batches/step-49/02-viewport-math.md) `mapViewportMath.ts` + `useMapViewport`
- [x] [49.03](./batches/step-49/03-map-viewport.md) `MapViewport` + `MapCanvas`
- [x] [49.04](./batches/step-49/04-pick-hover.md) `screenToMap` / pick-hover pipeline
- [x] [49.05](./batches/step-49/05-labels-reset.md) live zoom → labels; viewport reset
- [x] [49.06](./batches/step-49/06-edge-cases.md) resize, `mapSize` load, middle-click
- [x] [49.07](./batches/step-49/07-docs-verify.md) STAGING + manual QA

### M4 — Access ([step-41](./batches/step-41/00-index.md)) — **done**

- [x] [41.01](./batches/step-41/01-planning-lock.md) planning lock
- [x] [41.02](./batches/step-41/02-ps-map-registry.md) `maps.yml` + route guards
- [x] [41.03](./batches/step-41/03-staff-session.md) profile session + `permission_flags`
- [x] [41.04](./batches/step-41/04-frontend-gate.md) nav + error states
- [x] [41.05](./batches/step-41/05-docs-verify.md) STAGING + manual QA

### M5 — Settlements ([step-42](./batches/step-42/00-index.md)) — **done**

- [x] SF settlement core, setcapital, territory, relocate, departure hooks
- [x] `map_markers` export + PS `GET /data/markers` + centroid enrich
- [x] TFMCWeb gateway for SF map HTTP
- [x] Population + `marker_size` export; FE settlement marker layer

### M5b — Province grid + installations ([step-54](./batches/step-54/00-index.md)) — **done**

- [x] PS admin script → `province_id_grid.bin.gz`
- [x] SF `ProvinceGrid` + local `getProvince` (no HTTP)
- [x] SF installations + `/faction construct`
- [x] PS/FE `installations[]` markers on map
- [x] SF docs: `Installations.md`, `ProvinceGrid.md`

### M5c — Installation economy + GUI ([step-55](./batches/step-55/00-index.md))

- [x] [55.01](./batches/step-55/01-planning-lock.md) planning lock
- [x] [55.02](./batches/step-55/02-config-loader.md) config loader (`daily-upkeep`, `construction-time`)
- [x] [55.03](./batches/step-55/03-construction-queue.md) construction queue (max 1, tick, persist)
- [x] [55.04](./batches/step-55/04-upkeep-ledger.md) `Cashflow.INSTALLATIONS` + pay-or-destroy (cheapest first)
- [x] [55.05](./batches/step-55/05-installations-gui.md) faction GUI + confirm deconstruct
- [x] [55.06](./batches/step-55/06-docs-verify.md) docs + STAGING

### M6 — Forts ([step-43](./batches/step-43/00-index.md))

- [x] [43.01](./batches/step-43/01-planning-lock.md) planning lock
- [x] [43.02](./batches/step-43/02-sf-forts-export.md) SF `forts[]` + `zoc_provinces` export
- [x] [43.03](./batches/step-43/03-ps-zocgen.md) PS zocgen + static route + markers enrich
- [x] [43.04](./batches/step-43/04-frontend-zoc-hover.md) FE fort hover hatch overlay
- [x] [43.05](./batches/step-43/05-docs-verify.md) docs + STAGING

### M7 — Wars ([war-build-order.md](../war-build-order.md))

- [x] [44.01](./batches/step-44/01-planning-lock.md) planning lock — [Wars.md](../../simplefactions/Documentation/Wars.md)
- [x] War build order locked (steps 56–68 + 44)
- [x] [56.01](./batches/step-56/01-planning-lock.md) planning lock
- [x] [56.02](./batches/step-56/02-domain-model.md) domain model v2
- [x] [56.03](./batches/step-56/03-goal-validation.md) goal validation
- [x] [56.04](./batches/step-56/04-persistence.md) persistence
- [x] [56.05](./batches/step-56/05-declare-flow.md) declare flow
- [x] [56.06](./batches/step-56/06-participants.md) participants
- [x] [56.07](./batches/step-56/07-war-id-stubs.md) war_id stubs
- [x] [56.08](./batches/step-56/08-admin-commands.md) admin commands
- [x] [56](./batches/step-56/00-index.md) war foundation (56.01–56.09)
- [x] [57.01](./batches/step-57/01-planning-lock.md) planning lock
- [x] [57.02](./batches/step-57/02-pathfinder.md) pathfinder
- [x] [57.03](./batches/step-57/03-campaign-line.md) campaign line
- [x] [57.04](./batches/step-57/04-integration.md) integration
- [x] [57.05](./batches/step-57/05-docs-verify.md) docs verify
- [x] [57](./batches/step-57/00-index.md) pathfinder & campaign (57.01–57.05)
- [x] [58.01](./batches/step-58/01-planning-lock.md) planning lock
- [x] [58.02](./batches/step-58/02-domain-model.md) domain model
- [x] [58.03](./batches/step-58/03-progression-core.md) progression core
- [x] [58.04](./batches/step-58/04-occupation-zone.md) occupation zone
- [x] [58.05](./batches/step-58/05-campaign-gui.md) Campaign GUI
- [x] [58.06](./batches/step-58/06-integration.md) integration
- [x] [58.07](./batches/step-58/07-docs-verify.md) docs verify
- [x] [58](./batches/step-58/00-index.md) initiative & occupation (58.01–58.07)
- [x] [59.01](./batches/step-59/01-planning-lock.md) battle scheduling planning lock
- [x] [59.02](./batches/step-59/02-domain-model.md) battle scheduling domain model
- [x] [59.03](./batches/step-59/03-vote-tally.md) vote tally services
- [x] [59.04](./batches/step-59/04-schedule-orchestration.md) schedule orchestration
- [x] [59.05](./batches/step-59/05-campaign-gui.md) Campaign GUI hour toggles
- [x] [59.06](./batches/step-59/06-scheduler-integration.md) scheduler tick + warschedule
- [x] [59.07](./batches/step-59/07-docs-verify.md) docs verify
- [x] [59](./batches/step-59/00-index.md) battle scheduling (59.01–59.07)
- [x] [60.01](./batches/step-60/01-planning-lock.md) province presence + battle type planning lock
- [x] [60.02 province presence](./batches/step-60/02-province-presence.md) province presence tracker
- [ ] [60.03–60.10](./batches/step-60/00-index.md) Warbands merge & battle runtime
- [x] [61](./batches/step-61/00-index.md) military & casualties (61.01–61.07)
- [x] [61b](./batches/step-61b/00-index.md) battle dev mode (solo staging)
- [ ] SF steps 62–67
- [ ] [68](./batches/step-68/00-index.md) declare codes (last)
- [ ] PS step 44 map layer (after SF 67)

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
29. **Staff maps / Step 41** — **done** ([step-41](./batches/step-41/00-index.md); tick [STAGING](../STAGING.md) Step 41 when ready)  
30. **Settlements / Step 42** — **done** ([step-42](./batches/step-42/00-index.md))  
31. **Province grid + installations / Step 54** — **done** ([step-54](./batches/step-54/00-index.md))  
32. **Installation upkeep + construction + GUI / Step 55** — **done** ([step-55](./batches/step-55/00-index.md))  
33. **Wars, chronicle, wealth / Steps 44–46** — **44.01 lock done**; **SF war P1** next ([Wars.md](../../simplefactions/Documentation/Wars.md))  
34. Tick [STAGING](../STAGING.md) Steps 17–35, 31 when ready  
35. SimpleFactions map HTTP via TFMCWeb — **done** ([42.07](./batches/step-42/07-sf-tfmcweb-gateway.md))  

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

Post-MVP later: Discord multi-view 3D review bake (after [step-16](./batches/step-16/00-index.md) site viewer).  
Steps 17–35 **done** (code). Step 36 map platform planning lock **done**. **Step 37 code done (37.01–37.06).** **Step 38 parchment pipeline done (38.01–38.05).** **Step 39 ink cartography done (39.01–39.06).** **Step 40 nation labels done (40.01–40.09).** **Steps 47–49 done (code).** **Step 41 staff map access done (41.01–41.05).** **Step 42 settlements done (42.01–42.10).** **Step 54 province grid + installations done (54.01–54.06).** **Step 55 installation economy + GUI done (55.01–55.06).** **Step 43 fort ZOC done (43.01–43.05).** **Step 56.01 war foundation planning lock done.** **Step 56.02 domain model v2 done.** **Step 56.04 persistence done.** **Step 56.05 declare flow done.** **Step 56.06 participants done.** **Step 56.07 war_id stubs done.** **Step 56 war foundation done (56.01–56.09).** **Step 57 pathfinder & campaign done (57.01–57.05).** **Step 58.06 integration done.** **Step 58 initiative & occupation done (58.01–58.07).** **Step 59.01 battle scheduling planning lock done.** **Step 59.02 domain model done.** **Step 59.04 schedule orchestration done.** **Step 59.06 scheduler + warschedule done.** **Step 59.07 docs verify done.** **Step 59 battle scheduling complete.** **Step 60.02** province presence tracker **done**. **Next build:** SF war **60.03** warbands merge. Steps 45–46 **planned** ([16-map-platform.md](./16-map-platform.md)).
