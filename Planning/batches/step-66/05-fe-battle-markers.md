# Step 66.05 — FE battle markers + hover

**Repo:** `ProvinceSystem/frontend`  
**Depends on:** [66.04 FE campaign line](./04-fe-campaign-line.md)  
**Touches:** `public/battle.png`, `app/lib/mapMarkers.ts`, `app/components/map/MapMarkerLayer.tsx`, `MapViewer.tsx`

## Goal

Place **`battle.png`** icons at every scheduled battle province (invasion + counter legs) with hover tooltips showing battle kind and status.

## Build

| File | Action |
|------|--------|
| `public/battle.png` | **Add** campaign battle icon asset |
| `app/lib/mapMarkers.ts` | `kind === "battle"` → `/battle.png`; smaller default scale |
| `app/lib/warBattleMarkers.ts` | **New** - `wars[]` → `MapMarker[]` with stable ids `war-{id}-slot-{leg}-{index}` |
| `app/lib/warBattleMarkers.test.ts` | Status → title string; dedupe province with two legs |
| `app/components/MapViewer.tsx` | Merge war battle markers into marker list when wars loaded |
| `app/hooks/useMapHover.ts` | Ensure battle markers participate in hover hit-test |

### Tooltip copy

| Field | Example |
|-------|---------|
| `label` | `Siege` |
| `title` | `Siege - Greenfort province - Next battle` |

Use plain ASCII hyphen separators (no em dash). Strip Minecraft hex from province names if needed.

### Next-battle highlight

When `status === "next"`:

- `MARKER_HOVER_SCALE` or fixed 1.1x base scale.
- Optional ring in `WarCampaignLineLayer` at same coords (coordinate in 66.04 if easier).

### Z-order

Battle markers below hovered settlement pins; above base political layer (match installation marker z-index rules).

## Verify

- [x] All schedule slots with valid `map_x`/`map_y` render pins.
- [x] Hover shows kind + status.
- [x] Counter-leg slots visible left of border.
- [x] Active leg "next" slot visually distinct.
- [x] Vitest green.

## Out of scope

- In-game campaign GUI changes
- Chronicle / occupation

## Next

[66.06 docs verify](./06-docs-verify.md)
