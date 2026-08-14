# Step 40.07 — Label visibility and drill scopes

**Repos:** `ProvinceSystem` frontend  
**Depends on:** [06-docs-verify](./06-docs-verify.md)

## Goal

Labels must render above political PNGs, only appear for map-visible nations, and use full-territory vs direct-holdings province sets when a suzerain is drilled into.

## Locked rules

| Rule | Choice |
|------|--------|
| Z-order | `LabelLayer` above political overlay PNGs; hover wash stays on top |
| Visibility | Label when `mapObjects` `main` or `_nested` entry is `visible: true` |
| Hidden vassals | No label while overlay hidden (e.g. Verdant City at overview) |
| Full borders | `main` visible → label from full `provinces[]` |
| Direct holdings | `main` hidden + `_nested` visible → suzerain label from `provinces[]` minus subject provinces |
| While drilled | All visible nations labeled; other independents keep full-border labels |
| Font size | No drill-tier hardcoding; `LABEL_FONT_SIZE` (28) for all |

## Build

| File | Action |
|------|--------|
| [`frontend/app/lib/mapLabels.ts`](../../../frontend/app/lib/mapLabels.ts) | Visibility helpers, `labelsForProvinces`, `computeVisibleNationLabels`, `scope` on `NationLabelSpec` |
| [`frontend/app/lib/mapLabels.test.ts`](../../../frontend/app/lib/mapLabels.test.ts) | Overview vs drill visibility + direct-holdings tests |
| [`frontend/app/components/MapViewer.tsx`](../../../frontend/app/components/MapViewer.tsx) | `computeVisibleNationLabels(..., mapObjects)` |
| [`frontend/app/components/map/MapCanvas.tsx`](../../../frontend/app/components/map/MapCanvas.tsx) | Move `LabelLayer` after political PNGs |

## Layer order (shipped)

```text
base img → pick canvas → province overlay (if any) → political PNGs → LabelLayer → hover overlay
```

## Verify

- [x] `npm test` passes (22 tests)
- [x] `npm run build` passes
- [ ] `/map/main` nation mode: Grand Drakhanate full-border label at overview
- [ ] Verdant City not labeled until Ctrl+drill into Drakhanate
- [ ] After drill: visible subjects labeled; Drakhanate uses direct holdings; other independents still labeled
- [ ] Labels visually on top of political PNGs
- [ ] Hover / drill / modal / pick unchanged

## Out of scope

- Dynamic font scaling by territory size
- Curved `textPath`
- Labels on non-nation map modes

## Status

**Done** (40.07).

## Next

[step-41 staff map access](../step-41/00-index.md).
