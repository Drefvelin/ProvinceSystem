# Step 71.05 — Muster & `/raid join`

**Depends on:** [71.04](./04-launch-gui.md)  
**Repo:** `simplefactions`  
**Status:** done (2026-08-25)

## Goal

60-second muster after launch: side broadcast, `/raid join <id>`, transition to fight phase.

## Tasks

1. Register `/raid join <raidId>` (tab-complete active muster/fight raids for player's coalition).
2. Validate: attacker coalition only during muster; not in any warband; raid in `MUSTER` state.
3. On confirm launch: chat all **online attacker coalition** members with raid id and countdown.
4. Scheduler: at `musterEndsAt` → `startFight` (71.07 hooks); if zero attackers joined, still start or cancel — **lock: start anyway** (leader may be sole attacker).
5. Late join during muster allowed; after muster only if fight started and player warband-free (optional: muster-only join — **lock: muster only** per 71.01).
6. Unit tests: join rejects warband members; join after muster rejected.

## Verify

```powershell
cd simplefactions; mvn test "-Dtest=CampaignRaidJoin*"
cd simplefactions; mvn test
```
