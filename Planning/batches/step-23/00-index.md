# Step 23 — Kit lore editor polish

**Repos:** `ProvinceSystem` · `Workspace/rpcharacters` · `frontend`  
**Depends on:** Step 21 kits UI ([step-21](../step-21/00-index.md)); Step 22 sheet ([step-22](../step-22/00-index.md))  
**Playbook:** [14-character-creator.md](../../14-character-creator.md)

## Goal

Polish the kit lore-item editor: coloured name + dark preview, inline lore formatting (TLibs-style), player/staff pickable skins with website PNG thumbs, namespace-aware skin merge, duplicate texture guard, and optional 3D upload. No pack / legacy sync.

## Locked rules

| Piece | Choice |
|-------|--------|
| Pick existing | Player’s applied skins (`staff=0`, same `player_uuid`, matching `base_set`) **OR** staff applied (`staff=1`, `category=i_tools`, matching `base_set`) |
| Missing PNG | Omit from `pickable_skins` if texture file missing on website disk |
| Preview source | Website `SKINS_DIR` only; character-auth texture GET |
| Staff IA | `ia.tfmc_armorshop:{slug}`; player `ia.tfmc_submissions:{slug}` |
| Upload | New skin; optional **3D** → `item_3d` + model + texture; else `handheld` 16×16 |
| Duplicate PNG | SHA-256; reject same player + `base_set` in pending/approved/applied |
| Name | `NameColourPicker` + `name_colours`; cap via `name_colour_stops` |
| Lore | Inline `§` / `&` / `#RRGGBB`; prepend `§7` when no leading colour |
| Out | Legacy `localmodel` / pack-only knives; worldwide pick; server pack sync |

## Suggested build order

1. **[01-pickable-preview-apply](./01-pickable-preview-apply.md)** — Pick filter + texture GET + `ia_namespace` apply  
2. **[02-customise-name-lore-hash](./02-customise-name-lore-hash.md)** — Colours, lore codes, hash, 3D bridge  
3. **[03-editor-ui](./03-editor-ui.md)** — FE preview / pick thumbs / 3D checkbox  
4. **[04-docs-verify](./04-docs-verify.md)** — Hubs + STAGING  

## Checkpoint

```text
pick my + staff i_tools knives with thumbs
  → name colours + inline lore preview + §7
  → duplicate PNG blocked → 3D optional
  → staff merge tfmc_armorshop / player tfmc_submissions
```

**Done when:** Editor matches locked UX; pick/apply correct namespaces; no missing-file picks; docs closed.

## Status

**23.01–23.04 done.** Operator [STAGING](../../../STAGING.md) Step 23 when ready; Phase 4 wardrobe as capacity allows.
