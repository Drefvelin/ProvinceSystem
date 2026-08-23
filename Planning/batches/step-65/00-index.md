# Step 65 — Naval battles & invasions

**Repo:** SF · [war-build-order.md](../../war-build-order.md)  
**Depends on:** [64](../step-64/00-index.md) (campaign schedule, fort control, zone removal) · **Next:** [70](../step-70/00-index.md) (then [66](../step-66/00-index.md) war map)

## Goal

Extend the step 64 battle schedule with **port ZOC naval battles** and **naval invasion** slots. Landing in enemy fort ZOC becomes a **siege**. War-aware ZOC on map export.

| In scope | Out of scope |
|----------|--------------|
| Port sea ZOC → `NAVAL` schedule slots | Inter-battle raids (71) |
| Sea crossing → `NAVAL_INVASION` field slots | Raid war type (67) |
| Invasion into fort ZOC → siege slot | Declare codes (69) |
| `ZocRealm` war controller filter on export | Map `wars[]` route export (66) |
| Drop coastal fort docs | |
| Per-battle installation pick (optional; defer if needed) | |

## Batches

| Batch | Doc | Status |
|-------|-----|--------|
| **65.01** | [01-planning-lock.md](./01-planning-lock.md) | **done** (2026-08-23) |
| **65.02** | [02-port-zoc-naval-slots.md](./02-port-zoc-naval-slots.md) | **done** (2026-08-23) |
| **65.03** | [03-naval-invasion-detection.md](./03-naval-invasion-detection.md) | **done** (2026-08-23) |
| **65.04** | [04-resolver-launch-siege-override.md](./04-resolver-launch-siege-override.md) | **done** (2026-08-23) |
| **65.05** | [05-campaign-gui.md](./05-campaign-gui.md) | **done** (2026-08-23) |
| **65.06** | [06-zoc-realm-export.md](./06-zoc-realm-export.md) | **done** (2026-08-23) |
| **65.07** | [07-docs-verify.md](./07-docs-verify.md) | **done** (2026-08-23) |

## Status

**Step 65 done** (2026-08-23). **Next:** [step 70](../step-70/00-index.md) (done) → [step 66 war campaign map](../step-66/00-index.md).

## Note on build order

Step 65 was split from the old "step 64 forts & naval" scope. It builds on the shared **schedule + fort siege** foundation from step 64. Naval slots use the same trim, initiative, resolver, and progression pipeline.
