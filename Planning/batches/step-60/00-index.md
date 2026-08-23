# Step 60 — Warbands merge & battle runtime

**Repo:** SF · [war-build-order.md](../../war-build-order.md) · [01-planning-lock.md](./01-planning-lock.md) · [Wars.md](../../../../simplefactions/Documentation/Wars.md)  
**Depends on:** [59](../step-59/00-index.md) · **Next:** [61](../step-61/00-index.md)

## Goal

Merge Warbands into SF, central province enter/leave tracking, staff battle templates, and auto campaign battles (field / siege / raid + naval variants) with join command and province-leave penalty.

## Locked (60.01)

| Topic | Rule |
|-------|------|
| Province tracker | **1s** poll all online players; single `PlayerProvinceEnterEvent` / `PlayerProvinceLeaveEvent` source |
| **Field** | Capture **points**; bounded to battle province (+ optional adjacent **sea** tile) |
| **Siege** | Contest **area** held for **3 min** default (staff GUI per template) |
| **Raid** | **No region limit**; scoring only at **target**; attackers **no respawn**; defenders **infinite** or **set lives** |
| Naval variant | Field + siege only: adjacent sea province traversable; attacker spawn on sea |
| Leave penalty | Field + siege: leave allowed set → **10s** → death → side spawn (via central tracker) |
| Start triggers | `SCHEDULED` at voted hour; `AUTORESOLVE_PENDING` immediate after live leader accept (59) |

## Batches

| Batch | Summary | Status |
|-------|---------|--------|
| [60.01 planning lock](./01-planning-lock.md) | Province tracker, battle type matrix, scope | **done** (2026-08-20) |
| [60.02 province presence](./02-province-presence.md) | 1s tracker + enter/leave events | **done** (2026-08-20) |
| [60.03 warbands merge](./03-warbands-merge.md) | Submodule move from `warbands/` | **done** (2026-08-20) |
| [60.04 battle domain](./04-battle-domain.md) | `BattleType`, template model (superseded by 60.05 JSON) | **done** (2026-08-20) |
| [60.05 YAML templates + create](./05-template-gui.md) | Named YAML templates, `/battle create type id`, optional template picker GUI | **done** (2026-08-20) |
| [60.06 field runtime](./06-field-runtime.md) | Capture points, bounds, join, leave penalty | **done** (2026-08-20) |
| [60.07 siege runtime](./07-siege-runtime.md) | Contest area + hold timer | **done** (2026-08-20) |
| [60.08 raid runtime](./08-raid-runtime.md) | Target-only, attacker elimination, defender modes | **done** (2026-08-20) |
| [60.09 schedule hook](./09-schedule-hook.md) | Schedule / autoresolve -> battle + join command | **done** (2026-08-20) |
| [60.10 docs verify](./10-docs-verify.md) | Tests + staging checklist | planned |

## Status

**60.09 done** (2026-08-20). **Next batch:** [60.10 docs verify](./10-docs-verify.md).
