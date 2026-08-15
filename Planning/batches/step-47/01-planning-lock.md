# Step 47.01 — Planning lock

**Plan + docs only.** Lock multi-mode labels and Calavorn province-layer scope before implementation batches 47.02–47.07.

**Repos:** Planning (+ `ProvinceSystem` for later batches)  
**Depends on:** [00-index](./00-index.md) · [step-40/01-planning-lock](../step-40/01-planning-lock.md)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md)

## Locked — label map modes

| Mode | Labels v47 | Region JSON | Province source |
|------|------------|-------------|-----------------|
| `nation` | **Yes** (unchanged) | `nation.json` | `provinces[]` + recursive `subjects[]` full realm |
| `county` | **Yes** | `county.json` | `provinces[]` on each entry |
| `duchy` | **Yes** | `duchy.json` | Roll up `titles[]` → counties → provinces |
| `kingdom` | **Yes** | `kingdom.json` | Roll up `titles[]` → duchies → counties → provinces |
| `empire` | **Yes** | `empire.json` | Roll up `titles[]` → kingdoms → … → provinces |
| `trade` | **Yes** | `trade.json` | `provinces[]` per guild (compile from `province_data.json`) |
| `terrain` | **No** | — | Overlay only; `useProvinceHover` |
| `fertility` | **No** | — | Overlay only |
| `prosperity` | **No** | — | Overlay only |

Rationale: terrain/fertility/prosperity are continuous scalar fields, not discrete political regions with names.

**Map scope:** `/map/main` only for v47 labels and new toolbar modes. `dev` labels optional later.

## Locked — layer model

Extends step 40 / 39 stack (shipped z-order as of 40.07 + hover polish):

| Layer | Source | On screen? | Pick? | Labels? |
|-------|--------|------------|-------|---------|
| Colour base | `input/{map}/map.png` | Yes — bottom | No | No |
| Province overlay | `mapdata/{terrain\|fertility\|prosperity}` | When mode active | No | No |
| Political PNGs | `regiongen` overlays | Yes — drill stack | No | No |
| Hover wash | `_hover` region PNG | Yes — `z-10` | No | No |
| **Label layer** | Frontend SVG | Yes — `z-15` | No | **Political modes only** |
| Pick reference | `mapdata/{mode}` hidden canvas | Opacity 0 — `z-20` | **Yes** | No |

```text
base → province overlay (if any) → political PNGs → hover wash (z-10) → LabelLayer (z-15) → pick canvas (z-20)
```

**Critical:** labels never touch pick maps or `regiongen` PNGs. Placement uses province centroids + label grid; **connected components** use `province_label_neighbors` (step 48) with fallback to strict `province_neighbors`.

## Locked — label algorithm reuse

No new placement algorithm. Reuse step 40 pipeline:

| Piece | Location |
|-------|----------|
| Connected components + diameter | [`mapLabels.ts`](../../../frontend/app/lib/mapLabels.ts) |
| Inset corridor search | [`labelBlobGeometry.ts`](../../../frontend/app/lib/labelBlobGeometry.ts) |
| Constants | `MIN_PROVINCES` (3), `MIN_PIXEL_AREA`, `LABEL_GLYPH_WIDTH_EM`, inset grid 512-wide |
| Hover | 1% scale on hovered region (`HOVER_OVERLAY_EXPAND`); labels above hover wash |
| Nation drill | 40.07 scopes + full-realm `subjects[]` union at overview |

Generalize entry point: `computeVisibleRegionLabels(mapType, …)` with mode-specific province resolution.

## Locked — title province rollup

Mirror backend [`colour_mapping.py`](../../../backend/src/scripts/util/colour_mapping.py) hierarchy:

```text
empire.titles[] → kingdom → duchy.titles[] → county.titles[] → county.provinces[]
kingdom.titles[] → duchy → county → provinces
duchy.titles[] → county → provinces
county → provinces (leaf)
```

### Implementation — Option A (locked)

**Frontend rollup** in `titleProvinces.ts` + `useTitleLayerData` hook. Compile-time denormalization of `provinces[]` onto title JSON is **deferred** (optional perf follow-up).

### Title id resolution (`resolveTitleProvinces`)

For each `titles[]` child id at the current entity:

1. Look up id in the **expected child tier** for the active map mode (see fetch matrix below).
2. If found and child has `titles[]`, recurse.
3. If found and child has `provinces[]` (county leaf), union those ids.
4. If not found at expected tier, **fall through to `county.json`** (handles incomplete holders e.g. `Letzebierg` → `Bockfiels` on kingdom map).
5. If still not found, skip id; `console.warn` in development builds only.

Pseudocode by active `mapType` for a top-level region `R`:

| `mapType` | `resolveTitleProvinces(R)` |
|-----------|----------------------------|
| `county` | `R.provinces` |
| `duchy` | ⋃ `resolveCounty(child)` for each `child` in `R.titles[]` |
| `kingdom` | ⋃ `resolveDuchy(child)` for each `child` in `R.titles[]` |
| `empire` | ⋃ `resolveKingdom(child)` for each `child` in `R.titles[]` |

Dedupe province ids before passing to `labelsForProvinces`.

### Fetch matrix (`useTitleLayerData`)

Reuse `GET /{map}/data/{file}` — no new API routes.

| Active `mapType` | Fetch in addition to active mode JSON |
|------------------|---------------------------------------|
| `county` | — |
| `duchy` | `county.json` |
| `kingdom` | `duchy.json`, `county.json` |
| `empire` | `kingdom.json`, `duchy.json`, `county.json` |

Cache per `mapId` for the session; invalidate on `mapType` change.

## Locked — trade province assignment

For each province in `province_data.json`:

1. Read `trade` object (guild id → `{ trade, production }`).
2. Dominant guild = max `trade` weight (same as [`trade_compiler.py`](../../../backend/src/scripts/compile/trade_compiler.py)).
3. Assign province id to that guild’s `provinces[]` in compiled `trade.json` (47.03 / 47.04).

Sea/water provinces: skip if no trade block (same as trade map paint).

## Locked — title visibility & drill

| Rule | Choice |
|------|--------|
| Title `overlord` / `subjects` | **Not in defines today** — do not invent for v47 |
| All title entries visible | Every entry with `rgb` in active mode JSON gets a label |
| Nation drill | Unchanged from 40.07 |
| Title drill | **Out of scope** — Ctrl+drill on kingdom map unchanged (no nested title reveal) |

## Locked — Calavorn province layers

| Layer | Data source | Spoof? |
|-------|-------------|--------|
| Terrain | `defines/main/provinces.txt` → `terrain_map.png` | **No** — data exists |
| Fertility | Same `provinces.txt` | **No** |
| Trade | `input/main/guilds.json` + `province_data.json` | **Yes** until SF export |
| Prosperity | `province_data.json` `prosperity` field | **Yes** (same file as trade) |

Spoof generator (47.03): deterministic script from province ids — assign trade weights across ~5–8 fake guilds; prosperity 0–100. Document as **non-canonical** in STAGING.

## Locked — frontend integration

| Piece | Location |
|-------|----------|
| Rollup lib | `frontend/app/lib/titleProvinces.ts` (new) |
| Generalized labels | Extend `mapLabels.ts` → `computeVisibleRegionLabels(mapType, …)` |
| Title layer fetch | `frontend/app/hooks/useTitleLayerData.ts` (new) |
| Toolbar | [`MapToolbar.tsx`](../../../frontend/app/components/map/MapToolbar.tsx) — remove `mapId === "dev"` guard for province modes |
| MapViewer gate | Label-mode allowlist: `nation`, `county`, `duchy`, `kingdom`, `empire`, `trade` |

## Locked — regen / API

| Change | File |
|--------|------|
| Allow `trade` for `main` | [`regeneration.py`](../../../backend/src/scripts/util/regeneration.py) |
| Call `process_trade("main")` | Same, when `input/main/guilds.json` exists |
| Trade compile `provinces[]` | [`trade_compiler.py`](../../../backend/src/scripts/compile/trade_compiler.py) |
| One-off map scripts | `terrain_mapmode.py`, `fertility_mapmode.py` with `MAP=main` |

API routes unchanged: `GET /{map}/mapdata/{mode}` → `output/{map}/maps/{mode}_map.png`.

## Locked — chronicle cross-reference (step 45)

[Step 45](../step-45/00-index.md) stores political **state JSON** per date. Client reuses the same `MapCanvas` + `LabelLayer` compositor. Title and trade modes run the same rollup at render time from that day’s compiled defines — no server-side label cache.

## Out of scope (step 47)

- Real SF trade/guild export for Calavorn (replace spoof when available)
- Title-map drill / nested title visibility
- Labels on `dev` map (optional later; geometry hook already supports `main`)
- Backend PNG label rasterization
- Compile denormalize `provinces[]` onto kingdom/duchy/empire JSON (Option B)
- Chronicle date slider UI (step 45)

## Verify

- [x] Label modes table covers all `MapMode` values with yes/no
- [x] Option A (frontend rollup) locked; Option B deferred
- [x] Layer model and z-order documented
- [x] Title id resolution + fetch matrix specified
- [x] Trade province assignment matches `trade_compiler`
- [x] Chronicle cross-ref to step 45
- [x] No open TBD / “pick one” decisions

## Status

**47.01 done.**

## Next

[02-calavorn-terrain-fertility](./02-calavorn-terrain-fertility.md).
