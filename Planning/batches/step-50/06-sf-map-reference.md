# Step 50.06 — Operator cutover (SF + live PS)

**Repos:** Operator — `Workspace/simplefactions` · live `ProvinceSystem` · `Workspace/tfmcweb`  
**Depends on:** [05-ps-frontend-registry](./05-ps-frontend-registry.md) deployed

## Goal

**You run this on cutover day** — not during repo prep batches 50.02–50.05. Flips live MC uploads and public map from Calavorn/S4 to Adavaar/S5.

## Not in scope for repo agents

Repo work keeps SF on `map-reference: dev` until you execute this checklist.

## Operator checklist

### SimpleFactions (live MC)

| Step | Action |
|------|--------|
| 1 | Set `plugins/SimpleFactions/config.yml` → `map-reference: main` |
| 2 | `enable-map: true`; TFMCWeb gateway configured |
| 3 | Restart SF or reload config; verify uploads target `main` |
| 4 | Trigger regen on live PS `main` after first upload |

### Live ProvinceSystem

| Step | Action |
|------|--------|
| 1 | Deploy repo with Adavaar on `main` (50.02–50.05 merged) |
| 2 | Ensure `input/main` has latest political JSON |
| 3 | `fullregen main` on production |
| 4 | Verify `/map/main` shows Adavaar nations + settlements |

### Optional: `dev` map id after cutover

Per [01-planning-lock](./01-planning-lock.md): staging mirror (A), Calavorn archive (B), or retire (C).

## Verify

- [ ] `map_markers.json` upload shows `"map_id": "main"`
- [ ] Public `/map/main` = Adavaar; anonymous access unchanged (step 41)
- [ ] Staff `/map/r3b1rth` behaviour matches chosen post-cutover policy

## Status

**Planned** — operator-only.

## Next

[07-docs-verify](./07-docs-verify.md).
