# Step 43 — War map layer

**Repos:** `Workspace/simplefactions` · `ProvinceSystem`  
**Depends on:** SF war rework · [step-38](../step-38/00-index.md)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md) — requirement 10

## Goal

Display active wars: frontlines, contested provinces, optional campaign markers. **Do not infer wars from territory diffs alone.**

## Locked rules

| Piece | Choice |
|-------|--------|
| Blocker | SimpleFactions war rework must export structured `wars` payload |
| Data | `wars[]` per [map-export-schema.json](../../assets/map-export-schema.json) |
| Render | War mode overlay: frontline edges, crosshatch, belligerent tint |
| Events | War start/end feed map chronicle ([step-44](../step-44/00-index.md)) |

## Batches (when step starts)

1. **01-planning-lock** — Confirm SF war API  
2. **02-sf-war-export**  
3. **03-ps-war-compile**  
4. **04-frontend-war-mode**  
5. **05-docs-verify** — STAGING Step 43  

## Status

**Planned.** **Blocked on SF war rework.**
