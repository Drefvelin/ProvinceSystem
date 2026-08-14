# Step 43 — Forts and zone of control

**Repos:** `Workspace/simplefactions` · `ProvinceSystem`  
**Depends on:** [step-42](../step-42/00-index.md) · SF forts feature  
**Playbook:** [16-map-platform.md](../../16-map-platform.md) — requirement 9

## Goal

Show forts on the map with zone of control: fort province plus one-ring neighboring provinces.

## Locked rules

| Piece | Choice |
|-------|--------|
| SF | Fort entity in factions plugin; export `forts` with `zoc_provinces` |
| ZOC | Fort province + adjacent provinces on province graph |
| Render | Fort icon + subtle ZOC tint distinct from nation fill |

## Batches (when step starts)

1. **01-planning-lock**  
2. **02-sf-forts-export**  
3. **03-ps-fort-layer**  
4. **04-frontend-zoc**  
5. **05-docs-verify** — STAGING Step 43  

## Status

**Planned.** Blocked on SF forts implementation.
