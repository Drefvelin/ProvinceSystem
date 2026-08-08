# Batch 7.03 — Flat item writers (`item` + `handheld`)

**Plan + build:** Single-item writers with `generate: true` and vanilla parents (trust IA for model JSON).

**Repo:** `Workspace/armourshop`

**Depends on:** [02-armor-writer](./02-armor-writer.md)

## Plan

1. Extend pack writer for kinds `item` and `handheld`:
   - One item id `{slug}`; texture `{slug}.png` (16×16)
   - `resource.generate: true`
   - `item` → `parent: item/generated` (or IA-equivalent)
   - `handheld` → `parent: item/handheld`
2. No per-skin model JSON files.
3. Fixtures for both kinds; assert YAML + texture path.

## Build

| File | Action |
|------|--------|
| Pack writer | `item` + `handheld` branches |
| Fixtures | one 16×16 PNG each |

## Verify

- Both kinds write one-item YAML with correct parent  
- No `.json` models emitted for these kinds  

## Out of scope

Grip templates; `large_handheld`; `generate: false`.
