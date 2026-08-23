# Step 59.06 - Scheduler integration + warschedule

**Repo:** `simplefactions`  
**Depends on:** [59.05 Campaign GUI](./05-campaign-gui.md) · [01-planning-lock.md](./01-planning-lock.md)

## Goal

Connect battle schedule orchestration to the live server: UTC hourly tick, admin `/faction warschedule` dev commands, dev quorum override, and declare-hook verification.

## Delivered

| Component | Role |
|-----------|------|
| `War/schedule/BattleScheduleLookups.java` | Online `uuidToFaction` + offline `memberNameToUuid` for quorum/tick |
| `War/schedule/BattleScheduleTickService.java` | Minute poll, once-per-UTC-hour gate; defender deadline + vote close on active `VOTING` wars; persist on change |
| `War/schedule/CloseVoteOptions.java` | `scheduled()` vs `admin(forceQuorum)` for tick vs admin close |
| `War/schedule/WarScheduleAdminService.java` | Pure admin subcommand logic |
| `War/schedule/WarScheduleAdminResult.java` | Success/error result for commands |
| `BattleScheduleService` extensions | `openVote`, `skipBattleDay`, `castSpoofVotes`, `applyScheduledInstant`, admin `closeVote` overload |
| `War.forceQuorumNextClose` | Persisted dev flag; cleared after close attempt |
| `ConfigLoader` + `BattleQuorumService` | `dev_min_players` override when key explicitly present in config |
| `CommandManager` + `TabCompletion` | `/faction warschedule <warId> <subcommand>` |
| `SimpleFactions.onEnable` | Starts `BattleScheduleTickService` after `WarManager.start()` |

## Declare hook

Already wired at declare via `WarManager.declareWar` -> `populateCampaign` -> `initScheduleState`:

- `battleSchedulePhase = VOTING`
- `battleDay = declareDate(UTC).plusDays(1)` when `first_battle_day_after_declare: true`
- Empty `battleVotes` map

Verified in `WarCampaignServiceTest.populateCampaign_buildsFullAxisWithCursorAtBorder`.

## Admin commands

Permission: `simplefactions.admin` (same as `warstatus` / `warpath`).

| Subcommand | Effect |
|------------|--------|
| `opencvote` | Force `VOTING`; clear scheduled targets |
| `closevote` | Run tally now (ignores vote-close hour; respects `forceQuorumNextClose`) |
| `skipday` | `battleDay +1` only |
| `castvote <hour> [attacker\|defender\|both]` | Spoof votes for eligible roster members |
| `forcequorum` | Next close bypasses quorum |
| `setscheduled <iso-instant>` | Jump to `SCHEDULED` (Step 60 prep) |

Mutating commands persist the war and echo `warstatus` JSON.

## Dev config

When `war.battle_voting.dev_min_players` is **explicitly set** and lower than `min_players`, quorum uses the dev threshold. Remove the key on production configs.

## Tests

- `BattleScheduleTickServiceTest`
- `WarScheduleAdminServiceTest`
- Extended `BattleScheduleServiceTest`, `BattleQuorumServiceTest`, `ConfigLoaderBattleScheduleTest`, `WarMapperTest`

## Out of scope (59.07+)

- Step 60 battle execution from `SCHEDULED` / `AUTORESOLVE_PENDING`
- Docs verify + staging checklist (59.07)
- Remove dev commands before prod ([DEV-SHORTCUTS.md](../../DEV-SHORTCUTS.md))

---

**Done** (2026-08-20). **Next batch:** [59.07 docs verify](./00-index.md) (TBD).
