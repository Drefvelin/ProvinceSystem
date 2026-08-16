# Step 50.01 — Planning lock

**Repos:** Planning  
**Depends on:** —

## Goal

Lock the S5 cutover: repo prep vs operator cutover, and how live political data flows in.

## Locked decisions

| Piece | Choice |
|-------|--------|
| Public map id | **`main`** unchanged — URL stays `/map/main` |
| Public display name | **Adavaar** (at cutover — batch 50.05) |
| World source | Copy Adavaar world from PS **`dev`** → **`main`** in repo (50.02) |
| Live political data | **Manual copy** from live PS `input/dev/*.json` → repo `input/main/` (50.03) |
| SF `map-reference` | Stays **`dev`** until **operator cutover** (50.06 — you run on live MC + PS) |
| `map_markers.json` `map_id` | Matches SF export (`dev`) until cutover; optional `main` in repo `input/main` for local API only |
| Frontend `MAP_BOUNDS.main` | **`6400`** at cutover (50.05; was `4096` Calavorn) |
| S4 archive in repo | **Skip** — authoritative Calavorn remains on live PS until you flip |

### Repo prep vs operator cutover

| Phase | Batches | Who |
|-------|---------|-----|
| Repo prep | 50.02–50.04 | Dev machine / PR — live PS unchanged |
| Public cutover | 50.05–50.06 | **You** deploy registry + flip SF `map-reference` + live PS |
| Close-out | 50.07 | Docs + STAGING |

### Files: world (50.02)

| Source (`dev`) | Destination (`main`) |
|----------------|----------------------|
| `defines/dev/provinces.txt` | `defines/main/provinces.txt` |
| `input/dev/map.png`, `provinces.png` | `input/main/` |
| Regenerated geometry | `defines/main/province_*.json` (+ `.bin.gz`) |

### Files: political (50.03)

Copy from **live PS server** `input/dev/` (what SF already uploaded):

- `nation.json`, `guilds.json`, `province_data.json`, `queue.json`, `map_markers.json`

Do **not** change SF config to seed repo data.

### `dev` after public cutover (pick at 50.06)

| Option | Use |
|--------|-----|
| **A — Staging mirror** | Staff clone of public `main` |
| **B — Calavorn archive** | Move live S4 assets into `dev`; staff browses S4 at `/map/r3b1rth` |
| **C — Retire** | Single public map |

## Verify

- [x] Adavaar world promoted to `main` in repo (50.02)
- [ ] Live PS `input/dev` JSON copied to `input/main` (50.03)
- [ ] Operator cutover policy chosen (A/B/C) before 50.06

## Status

**Done** (locked with 50.02 revision).

## Next

[03-seed-live-input](./03-seed-live-input.md) — political JSON from live PS.
