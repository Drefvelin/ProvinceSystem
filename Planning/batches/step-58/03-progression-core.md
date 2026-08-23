# Step 58.03 — Campaign progression core

**Step:** 58 · **Repo:** SF  
**Spec:** [01-planning-lock.md](./01-planning-lock.md) · [Wars.md](../../../../simplefactions/Documentation/Wars.md)

> **Superseded (runtime):** shipped `CampaignPhase` FSM and defender hold/counter-push in this batch were replaced by [step 62.02+](../step-62/00-index.md) (`CampaignCapabilityService`, `CampaignPostBattleChoiceService`). Tables below document what 58.03 shipped; do not re-implement from this doc.

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
| Offensive side (pools) | `INVASION` → attacker; `RETAKE` / `COUNTER_PUSH` → defender |
| **`initiativeHolder`** | Winner of last fought battle; declare starts attacker |
| Cursor (invasion) | Pushing side win +1, lose -1; win at objective → `RETAKE` |
| Cursor (retake) | Defender win → phase invasion + defender choice; attacker win retake → cursor -1 |
| Cursor (counter-push) | Defender win -1, lose +1 |
| Initiative fuel | -1 for side that held initiative entering each fought battle; postponed = 0 |
| First battle | `campaignBattlesFought == 0` → node at `cursorIndex` (border B) |
| Cadence | Later invasion targets: `cursorIndex + N` clamped to objective |
| Defender holds initiative | Yellow nodes: hold (cursor) + counter-push (left) until resolved |
| Defender hold | `initiativeHolder` → attacker; stay `INVASION` |
| Defender counter-push | `campaignPhase = COUNTER_PUSH`; holder stays defender |

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
