# Step 71 — Campaign raids (inter-battle)

**Repos:** `simplefactions` only  
**Depends on:** [step 78](../step-78/00-index.md) (raid window, battle day schedule), [step 59](../step-59/00-index.md) (vote close / battle day), [step 61c](../step-61c/00-index.md) (warband signup), [step 64](../step-64/00-index.md) (battle engine, no province fence)  
**Next:** [step 67](../step-67/00-index.md) (pillage war type — rename from "raid war")  
**Type:** Gameplay feature (installation-to-installation timed assaults between main battles)

**Status:** done

## Problem

| Issue | Root cause |
|-------|------------|
| No way to assault enemy installations between main battles | Step 71 stub; 78 only shipped raid window + committed-target API |
| Raid target rules too narrow | 78.07 filtered committed picks only; design now targets **all operational** enemy installations |
| Campaign warband vs raid join conflict | No raid warbands or signup lock during raid window |
| Installation structures always damageable | No vulnerability gating or post-raid repair embargo |
| Staff `BattleType.RAID` uses capture points | Campaign raids need timer-only fights |

## Goal

**Campaign raids:** faction leaders launch installation-to-installation assaults during the **19-20** raid call window on battle day. One raid per coalition side per day; one global raid at a time per war. 60s muster, 10m fight, attackers stage at **source** port/airport, defenders hold **target** installation. No plugin scoring — players judge success by damage done.

Planning lock: [01-planning-lock.md](./01-planning-lock.md).

**Not in scope:** [step 67](../step-67/00-index.md) **pillage war** (border settlement war type).

## Build order

```mermaid
flowchart LR
  lock[71.01 lock] --> state[71.02 raid state]
  state --> elig[71.03 source target]
  elig --> gui[71.04 launch GUI]
  gui --> muster[71.05 muster join]
  muster --> bands[71.06 raid warbands]
  bands --> fight[71.07 raid battle]
  fight --> signup[71.08 warband lock]
  signup --> damage[71.09 damage embargo]
  damage --> intruder[71.10 intruder]
  intruder --> verify[71.11 docs tests]
  verify --> vehicleRepair[71.12 vehicle repair]
```

## Batches

| Batch | Doc | Scope | Status |
|-------|-----|-------|--------|
| **71.01** | [01-planning-lock.md](./01-planning-lock.md) | Terminology, timeline, eligibility, flow, warbands, fight rules, persistence | done |
| **71.02** | [02-campaign-raid-state.md](./02-campaign-raid-state.md) | `CampaignRaid` model, war JSON fields, quota + mutex, battle-day reset | done |
| **71.03** | [03-source-target-eligibility.md](./03-source-target-eligibility.md) | `CampaignRaidEligibilityService`; supersede 78.07 committed filter for campaign raids | done |
| **71.04** | [04-launch-gui.md](./04-launch-gui.md) | Campaign view Start raid; two-page source → target GUI | done |
| **71.05** | [05-muster-join-command.md](./05-muster-join-command.md) | `/raid join`, muster timer, side broadcast, state machine | done |
| **71.06** | [06-raid-warbands.md](./06-raid-warbands.md) | Ephemeral atk/def warbands; leader promotion; defender auto-add on login | done |
| **71.07** | [07-raid-battle-runtime.md](./07-raid-battle-runtime.md) | `campaign_raid_template`, timer end, TP, horn/title, no capture point | done |
| **71.08** | [08-campaign-warband-lock.md](./08-campaign-warband-lock.md) | Block campaign warband signup 19-20; open 20-21 | done |
| **71.09** | [09-damage-repair-embargo.md](./09-damage-repair-embargo.md) | Installation vulnerability gating; 48h target repair lock from fight start | done |
| **71.10** | [10-intruder-province.md](./10-intruder-province.md) | Non-participants in target province take damage + warning | done |
| **71.11** | [11-docs-verify.md](./11-docs-verify.md) | `Wars.md`, `Installations.md`, `AGENTS.md`, 78 doc amendments, `mvn test` | done |
| **71.12** | [12-vehicle-repair-embargo.md](./12-vehicle-repair-embargo.md) | Berthed vehicle repair lock in battle/raid; 48h target berth + repair embargo | done |

## Locked decisions (71.01)

| Decision | Value |
|----------|-------|
| Name | **Campaign raid** (not pillage war) |
| Call window | **19-20** Paris; in-flight may overrun |
| Quota | **One per coalition side** per `battleDay`; retaliation allowed |
| Global mutex | **One active campaign raid** per war |
| Source | Own operational **port/airport** (any, not pick-required) |
| Target | Any enemy operational **port/airport/fort** |
| Muster | **60s** `/raid join` |
| Fight | **10 min** timer; `BattleEndReason.TIMER`; no winner scoring |
| Attacker TP | **Source** installation center at fight start |
| Defender TP | **None** at start; respawn at **target** center |
| Campaign warband signup | **Blocked** 19-20; **open** 20-21 |
| Repair embargo | **Target only**; from fight start; **48h**; repeat raids allowed |
| Vehicle repair / berth | Berthed vehicles cannot repair while installation is in **any** battle/raid; 48h **target** also blocks repair and personal-to-installation berth |
| Damage gating | Vulnerable during raid/battle only; bomb protect otherwise |
| Intruders | Damage + normal death outside raid participant set |
| Picks (78) | Battle vehicles + intel only; **not** raid target filter |

## Out of scope

- Pillage war (step 67)
- Raid damage scoring / chronicle
- Map export of active raids
- AngelChest integration
- Replacing staff manual raid battles

## Verify (every batch)

```bash
cd simplefactions && mvn test
```

## Done when

- [x] Planning lock and index exist (71.01)
- [x] Leaders can launch campaign raid source → target during call window
- [x] Muster, join, ephemeral warbands, fight timer work end-to-end
- [x] Campaign warband signup blocked during raid window
- [x] Installation damage gating + repair embargo on target
- [x] Intruder province penalty active during fight
- [x] Docs updated (including 78 raid-target clarification); `mvn test` green
- [x] Berthed vehicle repair and berth blocked during battle/raid and 48h target embargo
