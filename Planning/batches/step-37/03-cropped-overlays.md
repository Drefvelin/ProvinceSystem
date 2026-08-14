# Step 37.03 — Cropped region overlays

**Repos:** `ProvinceSystem` backend + frontend  
**Depends on:** [02-split-map-viewer](./02-split-map-viewer.md)

## Goal

Replace full-map transparent region PNGs with cropped assets + bbox metadata; position overlays with percentage offsets in the frontend.

## Plan

1. **Backend** [`regiongen.py`](../../../backend/src/scripts/mapgen/regiongen.py): track painted pixel bbox per region; save cropped PNG; persist `x, y, w, h` in mode JSON or sidecar index during compile/regen.
2. **API** — no new route if bbox folded into existing mode JSON the frontend already loads.
3. **Frontend** [`MapEngineContext.tsx`](../../../frontend/app/core/MapEngineContext.tsx): `mapObjects` carry `x, y, w, h` (default `0, 0, full, full`).
4. **`MapCanvas.tsx`**: position overlay `<img>` with percentage `left/top/width/height` per [04-map-performance.md](../../04-map-performance.md).
5. Full regen required after deploy (document in verify).

## Build

| File | Action |
|------|--------|
| `backend/src/scripts/util/overlay_metadata.py` | create — crop helper + JSON merge |
| `backend/src/scripts/mapgen/regiongen.py` | bbox crop + metadata |
| `backend/src/scripts/compile/*` or defines JSON | optional bbox fields on regions |
| `frontend/app/components/map/overlayStyle.ts` | percentage positioning helper |
| `frontend/app/core/MapEngineContext.tsx` | bbox on mapObjects |
| `frontend/app/components/map/MapCanvas.tsx` | positioned overlays |

## Verify

- [x] Region PNG file sizes drop vs full canvas (spot-check one nation after fullregen)
- [x] Overlays align with base map after regen
- [x] Hover/highlight still correct
- [x] Old full-size overlays still work if bbox missing (fallback)
- [x] `npm run build` passes

**Post-deploy:** run `fullregen` for each map so cropped PNGs and `overlay` fields exist in defines JSON.

## Out of scope

Parchment base (38); label layer (39).
