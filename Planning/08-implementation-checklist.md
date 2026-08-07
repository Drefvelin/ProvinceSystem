# 08 — Implementation checklist (full platform)

Cross-repo build order for map, skins, bot, and pack. Journeys: [12-end-to-end-flows.md](./12-end-to-end-flows.md). Roadmap tracks: [03-roadmap.md](./03-roadmap.md).

Repos: `ProvinceSystem` (`dev`) | `tfmc_bot` | `Workspace/armourshop` | `Workspace/simplefactions` | ItemsAdder contents.

---

## Sprint 0 — Docs

- [x] Platform Planning playbook (README + 01–12)

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

### S4 — ArmourShop apply

**Repo:** `Workspace/armourshop` — [10](./10-armourshop-itemsadder.md)

- [ ] Config URL/key/paths; code command; pull; write `tfmc_submissions` with kind/grip templates; shop YAML; LP; deferred reload; applied ack

**Done when:** Flow 2 complete in [12](./12-end-to-end-flows.md).

### S5 — Item 3D + shield + harden

- [ ] `item_3d` / `shield` API/UI + display-key validation + ArmourShop apply (shield blocking auto)
- [ ] Multi-view review bake for Discord; shared view-only site renderer
- [ ] Quotas, retention, reserved slugs, tier size caps

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
8. Cropped overlays / item_3d / SF config hygiene as capacity allows  

---

## Definition of “finished product” (platform MVP)

| Area | Criteria |
|------|----------|
| Map | Live SF → API → web works; realm card shows size; usable on phone |
| Skins | armor_set + item/handheld/large_handheld; exact sizes; naming; Discord PNG review; ArmourShop pack + LP |
| Bot | Skins review with sheets; ban DM/log + banned role add/clear |
| Ops | Local website demo without Paper; deferred IA reload when safe |

Post-MVP: item_3d, shield, full map overlay crop, brewery module, SF secret cleanup if not done.
