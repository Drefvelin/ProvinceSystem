# Step 40.03 — Layout lib

**Repos:** `ProvinceSystem` frontend  
**Depends on:** [02-map-geometry](./02-map-geometry.md)

## Goal

Pure TypeScript label layout: connected province components, graph diameter endpoints, segment geometry for SVG rendering in batch 04. No UI or API fetching in this batch.

## Build

| File | Action |
|------|--------|
| [`frontend/app/lib/mapLabels.ts`](../../../frontend/app/lib/mapLabels.ts) | `computeNationLabels` + graph helpers |
| [`frontend/app/lib/mapLabels.test.ts`](../../../frontend/app/lib/mapLabels.test.ts) | Vitest unit tests (synthetic graphs) |
| [`frontend/vitest.config.ts`](../../../frontend/vitest.config.ts) | Vitest config (`environment: node`) |
| [`frontend/package.json`](../../../frontend/package.json) | `vitest` devDependency + `npm test` |
| [`frontend/app/components/map/types.ts`](../../../frontend/app/components/map/types.ts) | `provinces?: number[]` on `RegionRecord` |

## Exported API

| Export | Role |
|--------|------|
| `MIN_PROVINCES` | **3** |
| `MIN_PIXEL_AREA` | **15000** |
| `LABEL_FONT_SIZE` | **28** (map pixels; batch 04) |
| `connectedComponents` | Nation province subset → components |
| `graphDiameterEndpoints` | Two-pass BFS diameter |
| `componentPixelArea` | Sum `pixel_count` |
| `labelAngleDeg` | Segment angle in `(-90, 90]` |
| `computeNationLabels` | Main entry → `NationLabelSpec[]` |

### `NationLabelSpec`

`nationId`, `componentIndex`, `text`, segment `x1/y1/x2/y2`, midpoint `cx/cy`, `angleDeg`.

Diameter endpoints returned in ascending province id order for stable output.

## Test

```bash
cd frontend
npm test
```

## Verify

- [x] `npm test` — 12 tests pass
- [x] `npm run build` passes
- [x] `computeNationLabels` exported with `NationLabelSpec`
- [x] Integration with `LabelLayer` ([04-frontend-layer](./04-frontend-layer.md))

## Out of scope

- `LabelLayer` / `MapCanvas`
- Fetching geometry from API
- Font / ink styling / zoom-hide

## Status

**Done** (40.03). Next batch: [04-frontend-layer](./04-frontend-layer.md).
