# Step 42.09 — Frontend settlement markers

**Repos:** `ProvinceSystem` frontend  
**Depends on:** [08-sf-marker-size-export](./08-sf-marker-size-export.md)

## Goal

Render settlement markers on `/map/{id}` at server-provided `map_x`/`map_y`, with fixed-size PNG icons and a **straight** name label under each pin. **Hide the entire marker** (icon + name) until zoom is high enough that the label font reads acceptably on screen.

## Assets (authoritative)

| File | Use |
|------|-----|
| `frontend/public/settlement_small.png` | Normal settlement, `marker_size === "small"` (or missing) |
| `frontend/public/settlement_large.png` | Normal settlement, `marker_size === "large"` |
| `frontend/public/capital_settlement_small.png` | Faction capital city, `marker_size === "small"` (or missing) |
| `frontend/public/capital_settlement_large.png` | Faction capital city, `marker_size === "large"` |

Next.js serves these as `/settlement_small.png`, `/settlement_large.png`, `/capital_settlement_small.png`, `/capital_settlement_large.png`.

### Icon selection (locked)

```text
kind === "faction_capital" ?
  marker_size === "large" ? capital_settlement_large : capital_settlement_small
: marker_size === "large" ? settlement_large : settlement_small
```

`kind` comes from SF export (`faction_capital` when `faction.capital == settlement.centerProvince`). Size tier still from API `marker_size` only — **not** a FE population threshold.

## Build

| File | Action |
|------|--------|
| `frontend/lib/map/api.ts` | `fetchMapMarkers(mapId)` → `GET /{mapId}/data/markers` with session Bearer when needed |
| `frontend/app/hooks/useMapMarkers.ts` | Load markers with map session (staff maps) |
| `frontend/app/lib/settlementMarkers.ts` | **Add** — constants, zoom gate, layout helpers |
| `frontend/app/components/map/MapSettlementMarkers.tsx` | SVG/canvas overlay: image + straight text label |
| `frontend/app/components/map/MapCanvas.tsx` | Render marker layer (above base map; nation labels unchanged) |
| `frontend/app/components/map/types.ts` | `SettlementMarker` (`population`, `marker_size`, `kind`, `map_x`, `map_y`, `name`) |

### Layout (v1 — locked)

```text
        [ PNG pin ]
      settlement name
```

| Piece | Rule |
|-------|------|
| Anchor | Pin **bottom center** on `(map_x, map_y)` |
| Label | Settlement `name` on one **horizontal** line directly under the pin — **no** arc, **no** collision avoidance, **no** water/land checks |
| Label colour | `#000000` (black) for v1 |
| Label font | Same family as map labels (Fraunces) or site sans — lock one weight in build |

### Fixed sizes (map space — lock constants in `settlementMarkers.ts`)

Sizes are in **map pixels** (scale with zoom like the terrain). Tune in batch; start points:

| Tier | Normal pin (map px) | Capital pin (map px) | Label `fontSize` (map px) |
|------|---------------------|----------------------|---------------------------|
| `small` | e.g. 20 × 20 | e.g. 20 × 20 (tune if art differs) | e.g. 10 |
| `large` | e.g. 32 × 32 | e.g. 32 × 32 | e.g. 14 |

Capital and normal pins may share dimensions; use separate constants if the art aspect ratios differ.

### Zoom visibility (locked)

- Do **not** render a settlement until its label would meet a minimum **on-screen** font size (same idea as nation labels: `fontSize * displayScale >= SETTLEMENT_LABEL_MIN_SCREEN_PX`).
- Reuse or mirror `shouldShowLabelAtScreenSize` from `mapLabels.ts` (`LABEL_MIN_SCREEN_PX` is **6** today); settlements may use a **higher** minimum if 6 px feels too small — lock `SETTLEMENT_LABEL_MIN_SCREEN_PX` in this batch (e.g. **8–10**).
- When hidden: **no** pin and **no** name (not icon-only at low zoom).
- No max-zoom fade for settlements in v1 (unlike large nation labels).

### UX summary

| Piece | Choice |
|-------|--------|
| Map modes | Nation + default political view (same as nation labels) |
| Tooltip | Optional: name + faction + `population` on hover (markers visible only when zoom gate passes) |
| Fixtures | Optional `fixtures/map_markers.json` for dev |

### Z-order

Markers draw above the parchment base. Overlap with water, coast, or nation labels is **acceptable** — no offset nudging in v1.

## Verify

```bash
cd frontend
npm test
npm run build
```

- [ ] `/map/main` — zoomed out: **no** settlement markers
- [ ] Zoom in past threshold: markers appear at `map_x`/`map_y`
- [ ] Small vs large PNG matches API `marker_size` for both normal and faction-capital art
- [ ] `kind === "faction_capital"` uses `capital_settlement_small` / `capital_settlement_large`
- [ ] Name is straight black text under pin (not curved)
- [ ] Markers over water/coast render without special casing
- [ ] `/map/dev` (staff) loads with Bearer
- [ ] No regression on pan/zoom (step 49) or nation labels

## Out of scope

- Chronicle events on capital move (step 45)
- Per-guild markers
- Label halos, collision avoidance, curved text
- Per-guild `guild_capital` marker variants (only `faction_capital` gets capital art)

## Status

**Done** (2026-08-15). API fetch, settlement marker layer, zoom gate, four PNG variants.

## Next

[10-docs-verify](./10-docs-verify.md)
