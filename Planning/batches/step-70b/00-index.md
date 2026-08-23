# Step 70b — Campaign schedule simplicity (placement + GUI)

**Repo:** SF (+ minor PS FE if export shape changes) · [war-build-order.md](../../war-build-order.md)  
**Depends on:** [70](../step-70/00-index.md) (dual-leg builder + trim), [64](../step-64/00-index.md) (schedule model), [66](../step-66/00-index.md) (map export)  
**Fixes:** Broken campaign GUI (axis filler tiles), misleading battle names, dev cadence too dense  
**Next:** Server smoke on live Brume vs Lantan; then [71](../step-71/00-index.md) or map FE follow-ups

## Problem (2026-08-23)

Step 70 shipped dual-leg schedules in data, but the campaign GUI still walks the **geographic axis** and invents `"Battle of Wilderness"` / `"Battle of Greenfort"` labels for provinces with **no** schedule slot. Players see 5+ fake battles; real schedule (e.g. siege + capital) is buried or out of order.

Separately, `provinces_between_battles: 1` on dev makes natural schedules huge before trim; counter-leg wilderness fights (Brume capital approach) are correct in theory but untested on the live axis.

## Goal

**Dead simple contract:**

1. At declare / `warpath` regen, build and **persist** the full trimmed schedule for **both** legs.
2. In-game campaign GUI shows **only** those saved slots, in schedule order (paginated). No per-province axis filler.
3. Field cadence = every **3** provinces along each leg walk (config).
4. Display names use first / second / third … per **location name** (settlement, fort, wilderness key).
5. Map JSON export matches war JSON (both legs, all slots, status).

```text
center = border B (cursor at declare)

invasion:  B ──every 3 tiles──► objective   (+ sieges, naval, required terminal)
counter:   B-1 ──every 3 tiles──► atk_cap   (+ sieges, naval, required terminal)
```

## Batches

| Batch | Doc | Status |
|-------|-----|--------|
| **70b.01** | [01-planning-lock.md](./01-planning-lock.md) | **done** (2026-08-23) |
| **70b.02** | [02-cadence-config.md](./02-cadence-config.md) | **done** (2026-08-23) |
| **70b.03** | [03-schedule-only-gui.md](./03-schedule-only-gui.md) | **done** (2026-08-23) |
| **70b.04** | [04-battle-display-names.md](./04-battle-display-names.md) | **done** (2026-08-23) |
| **70b.05** | [05-export-align.md](./05-export-align.md) | **done** (2026-08-23) |
| **70b.06** | [06-docs-verify.md](./06-docs-verify.md) | **done** (2026-08-23) |

## Out of scope

- Pathfinder / axis geometry changes
- Changing `max_battles_per_leg` (stays 4)
- Live-war migration (re-declare or `/faction warpath` regen)
- Map FE spline / marker polish (separate 66 follow-up unless export adds `display_name`)

## Status

**Complete** (2026-08-23). All batches 70b.01–70b.06 done. **Next:** Server smoke on live Brume vs Lantan; then [71](../step-71/00-index.md) or map FE follow-ups.
