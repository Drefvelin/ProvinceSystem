# Step 30 — Character skin wardrobe (Phase 4 / E4)

**Repos:** `ProvinceSystem` (FE + BE) · `Workspace/rpcharacters` · (optional) MineSkin free API key  
**Depends on:** Phase 1 character session + roster ([step-19](../step-19/00-index.md)) · permission groups ([permission-groups.yml](../../../../Workspace/rpcharacters/src/main/resources/permission-groups.yml))  
**Playbook:** [14-character-creator.md](../../14-character-creator.md)

## Goal

Per-character **player skin wardrobe**: optional Mojang-signed skins (base + rank extras + masked), managed on the website, quick-swapped in-game, applied on character switch / join, auto-swapped while wearing an RP mask. Separate from item `/skins` and kit customise.

## Locked rules

| Piece | Choice |
|-------|--------|
| Slots | **base** (everyone) · **masked** (everyone, not manually selectable) · up to **2 extras** for donators |
| Slot counts (`wardrobe-skin-slots` = swappable skins) | Default **1** · Noble **1** · Gilded **2** · Ascended **3** · Legacy **3**. All ranks also get **masked** |
| Active slot | Persist which swappable slot is equipped (`base` / `extra_1` / `extra_2`). Never `masked` |
| Rank downgrade | **Wipe** slots above new max; if active pointed at wiped slot → fall back to `base` (or “no wardrobe skin” if base empty) |
| Empty base | Upload **optional**. No skin on base → **no** auto-apply on switch (leave account/Mojang look) |
| Model | **Detect** slim vs classic from PNG (no player picker required) |
| PNG | **64×64 only** (reject legacy 64×32 and other sizes) client + API |
| Review | **None** — Save → MineSkin sign → store → ready. Not Discord `/skins` review |
| MineSkin | Free tier + **free API key** (rate limits OK). Key in PS backend env/secrets |
| Skin ownership | RPC wardrobe **wins** over LibsDisguises / other skin setters |
| Re-apply | On **join**, on **character switch**, and on **mask equip/unequip**. No extra death/world re-apply unless something else clears the profile |
| Web UX | Standing frame slots; locked slots red hue + “needs {rank}+” using synced `display-name` colours; click unlocked slot → modal (pick PNG, 3D preview, Save) |
| Save UX | Save triggers MineSkin; show **Uploading…** spinner until signed data stored; then close/success |
| In-game | `/rpcharacterwardrobe` quick-swap among unlocked **filled** swappable slots (not masked) |
| Creation | **Platform-gated stages**: game = tip “edit wardrobe on the website”; web = wardrobe upload card. Need `platform: web \| game \| both` (default `both`) |
| Catalog | Sync `wardrobe-skin-slots` + group `display-name` (and tier) so web can lock slots and colour rank copy |

## Slot layout (UI)

```text
[ base ]  [ extra_1 ]  [ extra_2 ]     ← swappable; lock extras by rank
[ masked ]                              ← always available to upload; auto-only in game
```

- Default/Noble: only `base` + `masked` unlocked  
- Gilded: `base` + `extra_1` + `masked`  
- Ascended/Legacy: all four  

## Batches (implement in order)

1. **[01-planning-lock](./01-planning-lock.md)** — Hubs + locked table (this step)  
2. **[02-data-model-api](./02-data-model-api.md)** — PS schema + wardrobe REST (list / upload / clear / set active)  
3. **[03-mineskin-sign](./03-mineskin-sign.md)** — MineSkin v2 queue + free API key; PNG validate; slim detect  
4. **[04-ranks-platform-catalog](./04-ranks-platform-catalog.md)** — `wardrobe-skin-slots` perk; stage `platform`; catalog sync  
5. **[05-web-wardrobe-ui](./05-web-wardrobe-ui.md)** — Character wardrobe page + slot modal + spinner  
6. **[06-rpc-apply](./06-rpc-apply.md)** — Pull wardrobe; apply on join/switch; mask swap; `/rpcharacterwardrobe`  
7. **[07-creation-stages](./07-creation-stages.md)** — Web-only / game-only wardrobe stages wired end-to-end  
8. **[08-docs-verify](./08-docs-verify.md)** — Checklist + STAGING + handoff  

## Checkpoint

```text
web: upload base 64×64 → MineSkin → slot ready
  → set active / extras by rank (locked show Gilded+/Ascended+)
  → masked upload (not in wardrobe command)
game create: tip stage only; web create: wardrobe card
  → switch character / join → apply active (or skip if empty)
  → wear mask → masked skin; remove → active
  → /rpcharacterwardrobe → swap among filled unlocked slots
  → rank drop → extras wiped
```

**Done when:** Players can manage skins on the site, auto-apply on switch/join, mask-swap, and quick-swap in-game without staff review.

## Status

**30.01–30.08 done.** Step 30 complete (code). Operator STAGING ticks when live.
