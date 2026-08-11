# Step 21 — Kits + lore-item editor (Phase 3)

**Repos:** `Workspace/rpcharacters` · `ProvinceSystem` · `frontend` · `Workspace/armourshop` · Discord skinsreview  
**Depends on:** Step 20 kit plumbing ([step-20](../step-20/00-index.md)); player skins path (Discord → `tfmc_submissions` → `ps_items`)  
**Playbook:** [14-character-creator.md](../../14-character-creator.md) Phase 2 + 3

## Goal

1. **Generic kits** in `kits.yml` (not a hardcoded starter-only service). Claim via `/rpcharacter kit <kitId>`. Per-kit cooldown + once-per-character (or repeatable) from config.
2. **Web:** open an ALIVE character → Kits → kit → list all items, **Edit** only on `editable` lines. Customise **before claim**; once-per-character kits that are already claimed cannot be customised. Sync **all** kits + editable defs to the site.
3. Hold **whole kit claim** while that kit’s customise is `pending_skin`; on claim when `ready`, grant with skin+lore applied.

**Not in this step:** Ascended-only gate; staff curated / `tfmc_armorshop`; Mojang wardrobe (Phase 4); scraping `tfmc_pack`; tip/nudge copy (Discord owns player messaging).

## Locked rules

See [14-character-creator.md](../../14-character-creator.md) Phase 2 + 3. Summary:

| Piece | Choice |
|-------|--------|
| Config | `plugins/RPCharacters/kits.yml` — named kits; each has cooldown-hours, once-per-character (bool), items |
| Service | `KitService` (no StarterKit* hardcoding in code/copy) |
| Claim | `/rpcharacter kit <kitId>` with active character; no join/reload/create auto-grant |
| Cooldown | **Per kit** (player UUID × kit id); configured hours |
| Once-per-character | If true: at most one successful claim per character for that kit. If false: claim again after cooldown |
| Web entry | `/character` → ALIVE character detail (menu-like) → Kits → kit → Edit editable item |
| Not in create wizard | Knife/kit customise is **not** part of character creation |
| Editable | `skin-png` + `base-set` locked; player skin + RPC lore; NBT preview |
| Pending skin | Block claim for that kit+character until customise `ready` |
| Base knife (starter kit) | `IRON_HUNTING_KNIFE`; asset `assets/knife_skin.png` |

## Suggested build order

1. **[01–04](./01-editable-sync-and-preview.md)** — Editable sync, API, editor, apply — **done** (earlier product)
2. **[06-kit-claim-command](./06-kit-claim-command.md)** — Claim command cutover — **done** (starter-shaped; superseded by 08)
3. **[07-create-window-customise](./07-create-window-customise.md)** — Create-wizard customise — **done**; **superseded** by 09 (remove wizard path)
4. **[08-kits-yml-and-kit-service](./08-kits-yml-and-kit-service.md)** — Multi-kit `kits.yml` + `KitService` + per-kit claim/cooldown — **done**
5. **[09-kits-web-character-ui](./09-kits-web-character-ui.md)** — Character detail → kits UI; sync all kits; drop create-wizard customise — **done**
6. **[05-docs-verify](./05-docs-verify.md)** — Hubs + STAGING after 08–09 — **done**

## Checkpoint

```text
kits.yml → sync all kits → web character → kits → edit editable item
  → Discord if new skin → /rpcharacter kit <id> (block while pending_skin)
```

**Done when:** Multiple kits configurable; claim is generic; web character kits UI works; create wizard has no knife step; pending_skin blocks that kit’s claim; once-claimed once-per-character kits are not customisable.

## Status

**21.01–21.09 + 21.05 done** (21.07 superseded). Next product work: [step-22](../step-22/00-index.md) web character sheet; operator [STAGING](../../../STAGING.md) Step 20–21 when ready.
