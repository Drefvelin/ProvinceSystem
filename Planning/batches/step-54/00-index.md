# Step 54 — Province grid + installations

**Repos:** `Workspace/simplefactions` · `ProvinceSystem`  
**Depends on:** [step-53](../step-53/00-index.md) (one-province settlements) · [step-42](../step-42/00-index.md) (map markers)  
**Related:** [step-43](../step-43/00-index.md) (fort ZOC overlay — deferred until after 54)

## Goal

1. **Local province lookup** — O(1) block coord → province id from a prebuilt uint16 grid (no HTTP).
2. **Military installations** — place named forts, ports, and airports via `/faction construct`; show on map.
3. **No gameplay yet** — vehicles, upkeep, ZOC tint, siege routing deferred.

## Problem (today)

| Issue | Root cause |
|-------|------------|
| Every claim/setcapital pings PS | `RestServer.getProvince()` HTTP |
| Port proximity impossible at scale | No local spatial lookup |
| No forts/ports/airports | Not implemented |

## Paths (locked)

| Artifact | ProvinceSystem | SimpleFactions |
|----------|----------------|----------------|
| Source PNG | `backend/src/input/{map}/provinces.png` | — |
| RGB → id map | `defines/{map}/provinces.txt` | `Input/provinces.txt` |
| **Province ID grid** | `defines/{map}/province_id_grid.bin.gz` | `Input/province_id_grid.bin.gz` |
| Map export (output) | `input/{map}/map_markers.json` | `MapAPI/map_markers.json` |

**No `assets/` folder.** SF **Input** = read-only map data in; SF **MapAPI** = export/upload out only.

Grid missing on SF enable → **fail loud** (disable plugin).

## Build order

```mermaid
flowchart LR
  lock[54.01 lock] --> gridPS[54.02 PS grid script]
  gridPS --> gridSF[54.03 SF ProvinceGrid]
  gridSF --> install[54.04 SF installations]
  install --> markers[54.05 PS/FE markers]
  markers --> docs[54.06 docs verify]
```

## Batches

| # | Batch | Repo | Summary |
|---|-------|------|---------|
| 1 | [01-planning-lock](./01-planning-lock.md) | Planning | Grid format + installation rules — **done** |
| 2 | [02-ps-province-grid](./02-ps-province-grid.md) | PS | Admin script → `defines/.../province_id_grid.bin.gz` — **done** |
| 3 | [03-sf-province-grid](./03-sf-province-grid.md) | SF | Load grid from Input; replace HTTP lookup — **done** |
| 4 | [04-sf-installations](./04-sf-installations.md) | SF | Installation model + `/faction construct` — **done** |
| 5 | [05-ps-fe-markers](./05-ps-fe-markers.md) | PS + FE | Export + map marker icons — **done** |
| 6 | [06-docs-verify](./06-docs-verify.md) | SF + PS | Docs + smoke — **done** |

## Status

**Complete** (2026-08-18). Authoritative docs: [`Installations.md`](../../../../simplefactions/Documentation/Installations.md), [`ProvinceGrid.md`](../../../../simplefactions/Documentation/ProvinceGrid.md).

## Next

[step-55](../step-55/00-index.md) — installation upkeep + construction + GUI, then [step-43](../step-43/00-index.md) — fort ZOC.
