# Step 41 — Capitals and settlements on map

**Repos:** `Workspace/simplefactions` · `ProvinceSystem`  
**Depends on:** [step-38](../step-38/00-index.md) · [map-export-schema.json](../../assets/map-export-schema.json)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md) — requirement 8

## Goal

Faction and guild capitals (and distant guild settlements) must be **named in-game** in SimpleFactions, exported to PS, and rendered as town markers + labels on the map.

## Locked rules

| Piece | Choice |
|-------|--------|
| SF | `setcapital` + guild capital rules; settlement when guild capital > X blocks from faction capital |
| Export | `capitals` + `settlements` arrays per [map-export-schema.json](../../assets/map-export-schema.json) |
| Render | Icon + label at province centroid or `map_x`/`map_y` |
| Unnamed | No marker until named in-game |

## Batches (when step starts)

1. **01-planning-lock**  
2. **02-sf-export** — Capitals/settlements in upload payload  
3. **03-ps-compile** — Store in defines / serve via API  
4. **04-frontend-markers** — Town layer on map  
5. **05-docs-verify** — STAGING Step 41  

## Status

**Planned.**
