# Step 37.04 — Click interaction and hover data

**Repos:** `ProvinceSystem` frontend  
**Depends on:** [02-split-map-viewer](./02-split-map-viewer.md) (03 can parallel)

## Goal

Click opens nation modal with full data; Ctrl/Cmd+click drills; hover tooltip shows nation name; wire `size` / `subjects` / `overlord` in hover hook.

## Plan

1. **`useRegionHover.ts`** — extend `setRegionInfo` with `size`, `subject_size`, `overlord`, `subjects` from `regionData[id]`; tooltip text = region name (+ optional tier).
2. **`useMapHover.ts`** — rAF throttle mousemove; build RGB→id map once when `regionData` loads (replace `Object.keys().find` per move).
3. **`MapCanvas.tsx`** — `onClick`: if `ctrlKey` or `metaKey`, call drill handler; else open modal with `selectedRegionId`.
4. **`NationDetailModal.tsx`** — banner, tier, realm size, subjects list, description, overlord line; **Drill in** button when `subjects.length > 0`.
5. Remove drill from plain click path.

## Build

| File | Action |
|------|--------|
| `frontend/app/hooks/useRegionHover.ts` | full RegionInfo + name tooltip |
| `frontend/app/hooks/useMapHover.ts` | rAF + RGB map |
| `frontend/app/components/map/MapCanvas.tsx` | click routing |
| `frontend/app/components/map/regionInfo.ts` | create — `buildRegionInfo` |
| `frontend/app/components/map/NationDetailContent.tsx` | create — shared card body |
| `frontend/app/components/map/NationDetailModal.tsx` | full modal UX |
| `frontend/app/components/map/NationDetailPanel.tsx` | refactor — use shared content |

## Verify

- [x] Click nation → modal shows size and subjects when data exists
- [x] Ctrl+click drills as before
- [x] Tooltip shows nation name on hover
- [x] Hover feels smoother (no per-move key scan)
- [x] `npm run build` passes

## Out of scope

Mobile bottom sheet polish (37.05).
