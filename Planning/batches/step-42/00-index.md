# Step 42 — Capitals and settlements on map

**Repos:** `Workspace/simplefactions` · `ProvinceSystem`  
**Depends on:** [step-38](../step-38/00-index.md) · [map-export-schema.json](../../assets/map-export-schema.json)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md) — requirement 8

## Goal

Faction and guild capitals (and distant guild settlements) must be **named in-game** in SimpleFactions, exported to PS, and rendered as town markers + labels on the map.

## Locked rules

Spec: **`Workspace/simplefactions/Documentation/Settlements.md`** · [01-planning-lock](./01-planning-lock.md)

| Piece | Choice |
|-------|--------|
| SF | Named `Settlement` cities; `setcapital` found/join rules; explicit province lists |
| Export | `map_markers` sidecar per [map-export-schema.json](../../assets/map-export-schema.json) |
| Render | Marker at settlement centre coords (`centerX`/`centerZ`) |
| Map | One marker per settlement; faction capital on centre only when using existing city |

## Batches

1. **[01-planning-lock](./01-planning-lock.md)** — Naming, distance, export contract, SF package rules **done**
2. **02-sf-export** — `settlement` package + `Map.export`; per Settlements.md  
3. **03-ps-compile** — Store in defines / serve via API  
4. **04-frontend-markers** — Town layer on map  
5. **05-docs-verify** — STAGING Step 42  

## Status

**42.01 locked.** Next: SF export (42.02).
