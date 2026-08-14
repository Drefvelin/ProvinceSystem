# Step 37.02 — Split MapViewer

**Repos:** `ProvinceSystem` frontend  
**Depends on:** [01-planning-lock](./01-planning-lock.md)

## Goal

Extract monolithic [`MapViewer.tsx`](../../../frontend/app/components/MapViewer.tsx) into `components/map/*`; remove duplicate header, hero, and vote panel; apply TFMC site styling shell. **Behavior unchanged** until batch 04 (still click-to-drill).

## Plan

1. Create `frontend/app/components/map/types.ts` — `RegionInfo`, `MapId`, `MapMode`, props shared across map components.
2. **`MapPageLayout.tsx`** — page wrapper: title (map display name), flex/grid for canvas + side panel, `--tfmc-*` background.
3. **`MapCanvas.tsx`** — canvas ref, base map img, mapdata canvas, terrain/fertility overlays, hover img, `mapObjects` region layers; mousemove/mouseleave/click handlers passed as props.
4. **`MapToolbar.tsx`** — mode `<select>`, drill stack breadcrumb, reset view button.
5. **`NationDetailPanel.tsx`** — sidebar region card (modal wrapper in 37.04).
6. Refactor `MapViewer.tsx` to compose the above; keep export default for existing pages.
7. Remove: map-local sticky header, 350px banner, vote links sidebar block.

## Build

| File | Action |
|------|--------|
| `frontend/app/components/map/types.ts` | create |
| `frontend/app/components/map/MapPageLayout.tsx` | create |
| `frontend/app/components/map/MapCanvas.tsx` | create |
| `frontend/app/components/map/MapToolbar.tsx` | create |
| `frontend/app/components/map/drillUtils.ts` | create |
| `frontend/app/components/map/MapSidePanel.tsx` | create |
| `frontend/app/components/map/NationDetailPanel.tsx` | create (sidebar parity) |
| `frontend/app/components/MapViewer.tsx` | refactor to thin composer |

## Verify

- [x] `/map/main` loads; no duplicate header above `SiteHeader`
- [x] No hero banner or vote panel
- [x] Mode switch + hover + drill still work (pre-37.04 behavior OK)
- [x] `npm run build` passes

## Out of scope

Click vs Ctrl+click split (37.04); cropped overlays (37.03); mobile bottom sheet (37.05).
