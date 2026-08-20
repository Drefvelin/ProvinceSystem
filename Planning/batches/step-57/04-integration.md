# Step 57.04 — Campaign integration

**Step:** 57 · **Repo:** SF  
**Spec:** [03-campaign-line.md](./03-campaign-line.md) · [01-planning-lock.md](./01-planning-lock.md)

## Goal

Wire `WarCampaignService` into declare flow and admin tooling so campaign routes are generated at declare, persisted, and recomputable for debug.

## Scope

- [x] `declareWar`: set `subjectFactionId` for transfer wars; run `populateCampaign` before `addWar`
- [x] Declare fails (returns null) when campaign route cannot be generated
- [x] `WarManager.regenerateCampaign(War)` + package-visible overload for tests
- [x] Admin `/faction warpath <id>` - regen route + `warstatus` dump
- [x] Tab completion for `warpath`
- [x] Clearer DeclareWarView message when route generation fails
- [ ] Raid war type skips campaign (step 66 routes)

## Declare flow

1. Validate goal
2. Create `War`
3. Set `subjectFactionId` when `TRANSFER_SUBJECT`
4. `WarCampaignService.populateCampaign(war)` - skip for `WarType.RAID`
5. On failure: return `null` (war not added)
6. `addWar` (persists) + `commitForWar`

## Admin commands

| Command | Permission | Action |
|---------|------------|--------|
| `/faction warpath <id>` | Admin | Regenerate campaign route, persist, print summary + JSON |
| `/faction warstatus <id>` | Admin | JSON summary (includes campaign fields from 57.03) |

## Files

| File | Role |
|------|------|
| `Managers/WarManager.java` | Declare hook, `regenerateCampaign` |
| `Managers/CommandManager.java` | `warpath` subcommand |
| `Utils/TabCompletion.java` | `warpath` completion |
| `Managers/Inventory/DeclareWarView.java` | Route failure message |
| `Managers/WarManagerCampaignTest.java` | Regenerate tests |

## Verify

- [x] `mvn test` - all tests pass
- [x] Manual: declare subjugate war - `warstatus` shows campaign fields (war `0`, Brume vs Lantan, 2026-08-20)
- [ ] Manual: restart - `war_{id}.json` retains campaign fields
- [ ] Manual: `/faction warpath <id>` regenerates route

## Status

**Done** (2026-08-20). **Next batch:** [57.05 docs verify](./05-docs-verify.md).
