# Step 58.03 — Campaign progression core

**Step:** 58 · **Repo:** SF  
**Spec:** [01-planning-lock.md](./01-planning-lock.md) · [Wars.md](../../../../simplefactions/Documentation/Wars.md)

## Goal

Pure progression logic: cursor movement, initiative spend, phase FSM, retake loop, defender hold/counter-push, and next-battle node resolution. No GUI, occupation zone apply, white peace accept, or WarManager hooks yet (58.04-58.06).

## Scope

- [x] `campaignBattlesFought` field (persistence, mapper default `0`, reset at declare/regen)
- [x] `BelligerentRole` enum
- [x] `CampaignProgressionService` query + mutation API
- [x] `CampaignProgressionServiceTest` (16 cases)
- [x] Persistence test fixtures updated
- [x] `mvn test` — **64 tests**, 0 failures

## Rules implemented

| Area | Behavior |
|------|----------|
| Offensive side | `INVASION` → attacker; `RETAKE` / `COUNTER_PUSH` → defender |
| Cursor (invasion) | Win +1, lose -1; win at objective → `RETAKE`, holder attacker, no overshoot |
| Cursor (retake) | Defender win → holder defender, phase invasion; attacker win → cursor -1 |
| Cursor (counter-push) | Defender win -1, lose +1 |
| Initiative | -1 offensive side per fought battle; postponed = 0 |
| First battle | `campaignBattlesFought == 0` → node at `cursorIndex` (border B) |
| Cadence | Later invasion targets: `cursorIndex + N` clamped to objective |
| Attacker at 0 init | Yellow nodes: hold (cursor) + counter-push (left) |
| Defender hold | No state change |
| Defender counter-push | `campaignPhase = COUNTER_PUSH` |

## Files

| File | Role |
|------|------|
| `War/progression/BelligerentRole.java` | Attacker/defender role for offense |
| `War/progression/CampaignProgressionService.java` | Progression FSM + queries |
| `War/War.java` | `campaignBattlesFought` |
| `Database/WarData.java` | Gson field |
| `War/WarMapper.java` | Round-trip + legacy default |
| `War/WarDebugFormatter.java` | Debug JSON |
| `War/campaign/WarCampaignService.java` | Reset `campaignBattlesFought` in `initProgressionState` |

## Out of scope (58.04+)

- `OccupationService` (58.04)
- `WhitePeaceService` recalc/accept (58.05)
- `CampaignView` GUI (58.05)
- WarManager battle hook (58.06)
- Fort ZOC mandatory nodes (63)
- Capital-as-objective auto surrender (62)

## Status

**Done** (2026-08-20). **Next batch:** [58.04 occupation zone](./04-occupation-zone.md).
