# Step 43 — Forts and zone of control

**Repos:** `Workspace/simplefactions` · `ProvinceSystem`  
**Depends on:** [step-42](../step-42/00-index.md) · [step-54](../step-54/00-index.md) (placement + markers) · [step-55](../step-55/00-index.md) (operational forts only — upkeep + construction)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md) — requirement 9

## Goal

Show forts on the map with zone of control: fort province plus one-ring land neighbors, filtered to the **same top realm** as the fort holder. On fort marker hover, show a **precomputed diagonal hatch** overlay per fort.

## Locked rules

| Piece | Choice |
|-------|--------|
| SF | `installations[]` for pins (step 54); this step adds `forts[]` + `zoc_provinces` export |
| ZOC geometry | Fort province + land neighbors; exclude sea and unclaimed neighbors |
| ZOC political | Same **top realm** as fort owner (`getTopLiege` or faction id); war filter deferred |
| Render | Fort icon (step 54) + per-fort precomputed hatch PNG on hover (distinct from nation fill) |

## Build order

```mermaid
flowchart LR
  lock[43.01 lock] --> sf[43.02 SF export]
  sf --> ps[43.03 PS zocgen]
  ps --> fe[43.04 FE hover]
  fe --> docs[43.05 docs verify]
```

## Batches

| # | Batch | Repo | Summary |
|---|-------|------|---------|
| 1 | [01-planning-lock](./01-planning-lock.md) | Planning | Locked ZOC rules + hatch overlay + export — **done** |
| 2 | [02-sf-forts-export](./02-sf-forts-export.md) | SF | `forts[]` + `zoc_provinces` in `Markers.java` — **done** |
| 3 | [03-ps-zocgen](./03-ps-zocgen.md) | PS | Hatch asset + `zocgen` + static route + markers enrich — **done** |
| 4 | [04-frontend-zoc-hover](./04-frontend-zoc-hover.md) | FE | Fort hover → hatch overlay — **done** |
| 5 | [05-docs-verify](./05-docs-verify.md) | Both | `Installations.md`, STAGING Step 43, checklist — **done** |

## Status

**43.01–43.05 done** (2026-08-19). Fort ZOC hatch overlay shipped end-to-end (SF export → PS zocgen → FE hover). ZOC applies to **operational** forts only.

## Next

[step-44 war layer](../step-44/00-index.md) — blocked on SF war rework.
