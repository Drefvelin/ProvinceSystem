# Step 70c — Geographic campaign route GUI

**Repo:** SF · [war-build-order.md](../../war-build-order.md)  
**Depends on:** [70b](../step-70b/00-index.md) (schedule-only GUI, display names, export)  
**Fixes:** 70b.03 fight-order row (invasion then counter) misreads direction; pagination unnecessary  
**Next:** Server smoke on live Brume vs Lantan; then [71](../step-71/00-index.md)

## Problem (2026-08-23)

70b removed fake axis filler but ordered the route row as **fight order** (all invasion slots, then all counter slots). Counter wilderness battles appear after defender-side sieges; Greenfort siege reads as "toward attacker" when it is invasion-leg toward defender.

Players expect a **geographic axis row**: attacker capital side (left) → border B (first battle) → defender objective side (right).

## Goal

1. Merge both schedule legs; sort slots by `campaignProvinces` index ascending.
2. Single GUI row (slots 10-18); **no pagination** (`max_battles_per_leg` hard cap 4 → max 8 slots).
3. First-battle marker at border B (`cursor_index`), not invasion index 0 when those differ.
4. Remove `Counter-push schedule` lore.
5. Keep schedule-only tiles, 70b display names, and map export unchanged.

## Batches

| Batch | Doc | Status |
|-------|-----|--------|
| **70c.01** | [01-planning-lock.md](./01-planning-lock.md) | **done** |
| **70c.02** | [02-geographic-route-sort.md](./02-geographic-route-sort.md) | **done** |
| **70c.03** | [03-single-row-gui.md](./03-single-row-gui.md) | **done** |
| **70c.04** | [04-max-battles-cap.md](./04-max-battles-cap.md) | **done** |
| **70c.05** | [05-tests.md](./05-tests.md) | **done** |
| **70c.06** | [06-docs-verify.md](./06-docs-verify.md) | **done** |

## Out of scope

- Schedule builder / trim / cadence changes
- Axis filler tiles
- Map export leg ordering (JSON keeps separate arrays)

## Status

**Complete** (2026-08-23). All batches 70c.01–70c.06 done.
