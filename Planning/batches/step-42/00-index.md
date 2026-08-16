# Step 42 — Capitals and settlements on map

**Repos:** `Workspace/simplefactions` · `ProvinceSystem` · `Workspace/tfmcweb`  
**Depends on:** [step-38](../step-38/00-index.md) · [step-41](../step-41/00-index.md) · [step-35 HTTP gateway](../step-35/00-http-gateway-per-realm.md) · [map-export-schema.json](../../assets/map-export-schema.json)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md) — requirement 8

## Goal

Named **settlements** (cities) in SimpleFactions, exported to ProvinceSystem, rendered on `/map/{id}` with **small/large** PNG markers, straight name labels, and zoom-gated visibility — HTTP via **TFMCWeb**.

## Authoritative spec

**[`Workspace/simplefactions/Documentation/Settlements.md`](../../../../Workspace/simplefactions/Documentation/Settlements.md)**

Hub summary: [01-planning-lock](./01-planning-lock.md)

## Problem (today)

| Issue | Root cause |
|-------|------------|
| No cities on map | SF has province capitals only; no `Settlement` object or export |
| `setcapital` sets province only | No name, no territory, no map marker coords |
| Map has nation labels only | No marker layer in FE |
| SF talks HTTP directly | ~~RestServer bypasses TFMCWeb~~ — fixed in 42.07 |
| One marker size | No population tier or export field for large cities |

## Build order

```mermaid
flowchart LR
  lock[42.01 lock] --> core[42.02 SF core]
  core --> cap[42.03 setcapital + territory]
  cap --> reloc[42.04 relocate]
  reloc --> export[42.05 SF export]
  export --> ps[42.06 PS API]
  ps --> tw[42.07 TFMCWeb]
  tw --> size[42.08 size export]
  size --> fe[42.09 FE markers]
  fe --> docs[42.10 docs verify]
```

## Batches

| # | Batch | Repo | Summary |
|---|-------|------|---------|
| 1 | [01-planning-lock](./01-planning-lock.md) | Planning | Spec + package rules — **done** |
| 2 | [02-sf-settlement-core](./02-sf-settlement-core.md) | SF | `Settlement`, handler, persistence, `validate()` — **done** |
| 3 | [03-sf-setcapital-territory](./03-sf-setcapital-territory.md) | SF | Commands, found/join, claim/loss, dissolve — **done** |
| 4 | [04-sf-relocate](./04-sf-relocate.md) | SF | Relocate disband + destination rules — **done** |
| 4.1 | [04.1-sf-settlement-departure](./04.1-sf-settlement-departure.md) | SF | Departure hooks on `setCapital` / `removeGuild` — **done** |
| 5 | [05-sf-map-export](./05-sf-map-export.md) | SF | `map_markers.json` + `uploadAll` — **done** (via RestServer; cutover in 42.07) |
| 6 | [06-ps-markers-compile](./06-ps-markers-compile.md) | PS | Ingest upload, GET markers, centroid enrich — **done** |
| 7 | [07-sf-tfmcweb-gateway](./07-sf-tfmcweb-gateway.md) | SF + TW | Replace RestServer HTTP with TFMCWeb gateway — **done** |
| 8 | [08-sf-marker-size-export](./08-sf-marker-size-export.md) | SF + PS schema | Population + `marker_size`; config threshold — **done** |
| 9 | [09-frontend-markers](./09-frontend-markers.md) | PS FE | Four PNGs, straight labels, zoom gate — **done** |
| 10 | [10-docs-verify](./10-docs-verify.md) | Planning | STAGING + hub close-out — **done** |

## Status

**Step 42 complete** (42.01–42.10, 2026-08-15).

## Next (after step 42)

[step-43 forts](../step-43/00-index.md).
