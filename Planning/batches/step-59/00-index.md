# Step 59 — Battle scheduling

**Repo:** SF · [war-build-order.md](../../war-build-order.md) · [01-planning-lock.md](./01-planning-lock.md) · [Wars.md](../../../../simplefactions/Documentation/Wars.md)  
**Depends on:** [58](../step-58/00-index.md) · **Next:** [60](../step-60/00-index.md)

## Goal

Battle window, hourly voting (`min` rule), configurable vote/defender deadlines, postpone (votes persist), dual-leader autoresolve only.

## Locked (59.01)

| Topic | Rule |
|-------|------|
| Vote open | When next battle pending (declare or after battle end); no province required |
| Vote close | `vote_close_hour` on battle day (default **16**, config) |
| Defender choice | By `defender_choice_deadline_hour` (default **12**, config); else auto **Hold** |
| First battle day | **Day after declare** (UTC); voting starts at declare |
| Quorum | `min_players` **or** smallest-side-full (`pass_if_either: true`) |
| Postpone | `battleDay` +1, votes persist, no initiative |
| Hour pick | `min(attacker, defender)` per hour; tie → earliest |

## Batches

| Batch | Summary | Status |
|-------|---------|--------|
| [59.01 planning lock](./01-planning-lock.md) | Timeline, persistence, quorum, GUI, dev commands | **done** (2026-08-20) |
| [59.02 domain model](./02-domain-model.md) | Persistence + config + `BattleSchedulePhase` | **done** (2026-08-20) |
| [59.03 vote tally](./03-vote-tally.md) | Window, vote, quorum services + tests | **done** (2026-08-20) |
| [59.04 schedule orchestration](./04-schedule-orchestration.md) | Postpone, autoresolve, auto-Hold | **done** (2026-08-20) |
| [59.05 Campaign GUI](./05-campaign-gui.md) | Hour toggles + schedule info + autoresolve buttons | **done** (2026-08-20) |
| [59.06 scheduler + warschedule](./06-scheduler-integration.md) | Declare hook, tick, `warschedule`, dev quorum | **done** (2026-08-20) |
| [59.07 docs verify](./07-docs-verify.md) | Tests + staging checklist | **done** (2026-08-20) |

## Status

**Step 59 complete** (2026-08-20). **Next:** [60 - Warbands merge & battle runtime](../step-60/00-index.md).
