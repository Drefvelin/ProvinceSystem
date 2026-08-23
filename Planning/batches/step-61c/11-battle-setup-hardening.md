# Step 61c.11 - Battle setup hardening

**Code batch.** Bounds validation for FIELD/SIEGE setup, capture point delete in Point View GUI, and guaranteed campaign warband shell enrollment.

**Repo:** SF  
**Depends on:** [61c.10 battle side fast edit](./10-battle-side-fast-edit.md)

## Delivered

| Area | Change |
|------|--------|
| Bounds validation | `BattlePlacementValidator` checks spawns, jails, capture points, naval spawn, and siege contest corners against allowed provinces |
| Placement hooks | `BattleSideSetupService`, `BattleContestSetup`, commands, Side Edit GUI reject out-of-bounds locations when bounds are known |
| Start gate | `Battle.start()` returns an error string and blocks start when validation fails |
| Point delete | Point View click-to-delete; global letter ids renumbered after delete |
| Campaign warbands | `CampaignBattleRosterService.ensureEnrolled()` on create, load, existing-battle access, and scheduled/autoresolve start |

## Key paths

- `War/battle/engine/BattlePlacementValidator.java`
- `War/battle/engine/BattleCapturePoints.java` (`removePoint`, `compressGlobalLetters`, `syncLinearChain`)
- `War/battle/ui/BattleInventoryManager.java` (Point View delete affordance)
- `War/battle/campaign/CampaignBattleRosterService.java` (`ensureEnrolled`)

## Manual verify

1. Campaign battle with `provinceId` set: placing spawn/jail/point outside province is rejected.
2. Start battle with an out-of-bounds point blocked with clear message.
3. Point View: delete middle point renames remaining A/B/C lane correctly.
4. `/faction warschedule ... battlecreate` and server reload: both sides show faction warband shells in Side View.
