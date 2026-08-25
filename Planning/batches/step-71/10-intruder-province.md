# Step 71.10 — Intruder province penalty

**Depends on:** [71.07](./07-raid-battle-runtime.md)  
**Repo:** `simplefactions`  
**Status:** planned

## Goal

Attackers in the **target province** who are not active raid participants (or already eliminated) take fast damage and receive a leave warning. Normal death rules (no battle `keepInventory`).

## Tasks

1. Subscribe to `ProvincePresenceService` / province enter tick during active campaign raid fight.
2. For each attacker-coalition player in target installation's province:
   - If not in attacker raid warband OR marked out by `RaidAttackerEliminationService` → apply periodic damage + chat warning.
3. Do not apply to defenders or raid participants.
4. Config: `intruder_damage_interval_ticks`, `intruder_damage_amount` under `war.campaign_raid`.
5. Unit tests: participant exempt; eliminated attacker penalized; defender in province exempt.

## Verify

```powershell
cd simplefactions; mvn test "-Dtest=CampaignRaidIntruder*"
cd simplefactions; mvn test
```
