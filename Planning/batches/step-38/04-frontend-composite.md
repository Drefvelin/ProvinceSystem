# Step 38.04 — Frontend composite

**Repos:** `ProvinceSystem` frontend  
**Depends on:** [02-parchment-base](./02-parchment-base.md) · [03-muted-political](./03-muted-political.md)

## Goal

Map page composes correctly with parchment base + muted overlays; pick/hover/drill behaviour unchanged.

## Plan

1. **`MapCanvas.tsx`** — No URL change if backend serves parchment at `/{map}/map`; confirm `onLoad` still sets `mapSize` from natural dimensions.
2. **Overlay tuning** — Adjust static overlay + hover opacity (e.g. `opacity-70`–`opacity-75`) so muted fills read on parchment; avoid washing out borders.
3. **Province modes (`dev`)** — `terrain` / `fertility` / `prosperity`: keep `mapdata` colour overlay on top of parchment base (may need opacity tweak).
4. **Loading state** — Optional subtle improvement: show parchment-sized skeleton while base img loads (only if trivial; otherwise skip).
5. **Fallback** — Local dev without Xaero: `map.png` still works; no console errors.

## Build

| File | Action |
|------|--------|
| `frontend/app/components/map/MapCanvas.tsx` | opacity / layering tweaks |
| `frontend/app/components/MapViewer.tsx` | only if canvas `mapdata` URL needs cache-bust query after regen (unlikely) |

## Verify

- [ ] `/map/main` shows parchment terrain after backend regen + hard refresh (operator)
- [x] Hover highlight aligns with nation boundaries (bbox + mute) — opacity-only change; bbox math unchanged
- [x] Ctrl+drill stack overlays align and use muted colours — same overlay positioning
- [x] Click → modal still works — pick canvas untouched
- [x] Mobile layout unchanged ([step-37](../step-37/05-mobile-layout.md))
- [x] `npm run build` passes
- [x] Dev without parchment: page still loads with legacy base — same `/{mapId}/map` URL

## Status

**Done** (38.04 code). Operator visual pass on `/map/main` after fullregen recommended.

## Out of scope

Label layer ([step-40](../step-40/00-index.md)); wealth charts; new routes.
