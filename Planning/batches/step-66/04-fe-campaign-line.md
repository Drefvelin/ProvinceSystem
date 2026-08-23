# Step 66.04 — FE smooth campaign line

**Repo:** `ProvinceSystem/frontend`  
**Depends on:** [66.03 PS schema passthrough](./03-ps-schema-passthrough.md)  
**Touches:** `app/components/map/`, `app/lib/`, `app/hooks/useMapMarkers.ts`

## Goal

Render a **smooth dotted campaign line** with outlined stroke for each active war, following the campaign axis on the map canvas.

## Build

| File | Action |
|------|--------|
| `app/lib/warCampaignLine.ts` | **New** - waypoint build, Catmull-Rom → SVG path `d`, stroke style helpers |
| `app/lib/warCampaignLine.test.ts` | **New** - spline does not self-intersect on fixture; endpoints match waypoints |
| `app/components/map/WarCampaignLineLayer.tsx` | **New** - SVG overlay aligned to map pixel space |
| `app/components/map/MapCanvas.tsx` | Mount `WarCampaignLineLayer` when `wars.length > 0` |
| `app/components/map/types.ts` | `WarExport`, `WarScheduleSlot` types |
| `app/hooks/useMapMarkers.ts` | Parse and return `wars` from API |

### Waypoint source

Prefer `campaign_line_points[]` from API if present; else resolve `campaign_provinces` via loaded `centroids` in `MapViewer`.

Prefix with attacker capital coords; suffix not needed if axis includes objective.

### Visual spec (66.01 lock)

- Border path: solid, ~1.5x width of dash path, `#2a1810` or theme ink.
- Dash path: `stroke-dasharray` dotted, accent color (attacker-tinted or neutral campaign red).
- `vector-effect: non-scaling-stroke` or scale strokes with `displayScale` consistently with labels.

### Interaction

- Line is `pointer-events: none` (battles handle hover in 66.05).
- Optional: faint line always visible when wars active; no toggle required in v1.

## Verify

- [x] Line visible on dev map with test war export.
- [x] Line curves smoothly at province corners (visual QA).
- [x] Line hidden when no wars.
- [x] `npm test` / vitest green for spline util.

## Out of scope

- Battle pins (66.05)
- Occupation tint

## Next

[66.05 FE battle markers](./05-fe-battle-markers.md)
