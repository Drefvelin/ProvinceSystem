# Step 39.05 — Frontend overlay opacity

**Repos:** `ProvinceSystem` frontend  
**Depends on:** [03-earth-tone-fills](./03-earth-tone-fills.md) (can ship with 39.04)

## Goal

Drill-stack (visible `mapObjects`) overlays read slightly stronger than hover-only overlays, so drilled political view feels **committed** not ghosted — without overpowering the ink parchment base.

## Plan

1. **`MapCanvas.tsx`** — split constants:
   - `HOVER_OVERLAY_OPACITY` — default `0.72`–`0.75`
   - `DRILL_STACK_OVERLAY_OPACITY` — default `0.88`
2. **`HoverOverlayImage`** — use hover constant
3. **`mapObjects` `.map()`** — use drill constant
4. **Province modes** — keep `PROVINCE_MODE_OVERLAY_OPACITY` at `0.72` (dev terrain/fertility/prosperity)
5. **Visual pass** — if earth tones + ink base still too strong at 0.88, tune drill to `0.85`; document final values in this file

## Build

| File | Action |
|------|--------|
| `frontend/app/components/map/MapCanvas.tsx` | split opacity constants |

## Shipped values

| Constant | Value | Used for |
|----------|-------|----------|
| `HOVER_OVERLAY_OPACITY` | `0.72` | `HoverOverlayImage` |
| `DRILL_STACK_OVERLAY_OPACITY` | `0.88` | visible `mapObjects` drill stack |
| `PROVINCE_MODE_OVERLAY_OPACITY` | `0.72` | terrain / fertility / prosperity overlay |

## Visual acceptance

| Check | Pass when |
|-------|-----------|
| Hover only | Nation highlight visible but parchment shows through |
| After drill | Stack of realms readable; subjects not faint |
| Mobile | Same constants; no layout change |
| Province dev modes | Unchanged behaviour |

## Verify

- [x] `npm run build` passes
- [x] `HoverOverlayImage` still uses opacity `0` until loaded (`key={url}` unchanged)
- [ ] Manual: hover one nation → drill into subject → compare opacity

## Status

**Done** (39.05 code). Operator visual pass recommended.

## Out of scope

CSS blend modes (`multiply` on `<img>`) — defer unless opacity split insufficient; labels ([step-40](../step-40/00-index.md)).
