# Step 61c.01 — Campaign UX planning lock

**Repo:** SF · [00-index](./00-index.md) · **Blocks:** [61c.02](./02-template-settings-only.md)–[61c.05](./05-docs-verify.md)

## Goal

Lock product rules for template geometry, warschedule feedback, and campaign warband signup before code. No Java in this batch.

---

## Locked — battle templates (settings only)

| Rule | Detail |
|------|--------|
| **Purpose** | Named **rule presets**: lives, life type, friendly fire, keep inventory, teleport-on-start default, siege contest **duration**, raid defender respawn mode, naval variant flag |
| **Not in template** | Spawns, jails, capture point coordinates, contest area bounds, raid target location |
| **Campaign create** | [`BattleFactory.applyCampaignDefault`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/engine/BattleFactory.java) applies **settings only**; battle sides exist with empty layout |
| **Staff manual battles** | [`BattleFactory.applyTemplate`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/engine/BattleFactory.java) applies **settings only** (same split); staff use `/battle edit` for geometry |
| **YAML** | [`battle-templates.yml`](../../../../simplefactions/src/main/resources/battle-templates.yml) drops coordinate blocks; keep type + numeric/boolean fields |
| **Collective lives** | Still overridden at `battle.start()` by 61.04 for campaign; template `lives` is fallback for manual battles only |

Rationale: campaign battles are tied to a **province**; geometry is placed per battle in-world, not copied from dummy coords in YAML.

---

## Locked — `/faction warschedule` feedback

| Rule | Detail |
|------|--------|
| **On success** | Show **one short formatted block** relevant to the subcommand (plain chat lines, not JSON) |
| **On error** | Single red line (unchanged) |
| **`/faction warstatus`** | Keeps full [`WarDebugFormatter`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/WarDebugFormatter.java) JSON for deep debug |
| **No duplicate dump** | Remove post-success `formatStatusLines` loop from warschedule handler |

### Per-subcommand fields (minimum)

| Subcommand | Show |
|------------|------|
| `opencvote` | War id, `battleSchedulePhase`, `battleDay` |
| `closevote` | Result outcome (scheduled / postponed / autoresolve pending), `scheduledBattleAt`, `scheduledBattleProvinceId`, `battleSchedulePhase` |
| `castvote` | Hour, selections added, distinct voter count, current phase |
| `skipday` | New `battleDay` |
| `forcequorum` | Confirmation that next close bypasses quorum |
| `setscheduled` | `scheduledBattleAt`, `scheduledBattleProvinceId`, phase |

Optional second line: battle id if campaign battle already exists (`BattleManager.getByWarId`).

---

## Locked — campaign warband auto-create + signup

Applies when `battle.warId != null` and warband created by [`CampaignBattleRosterService`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/campaign/CampaignBattleRosterService.java).

### Auto (system)

| Step | Behavior |
|------|----------|
| Battle prep | One **faction warband shell** per main participant on each side (id = main faction id) |
| Battle enrollment | Shell warband **auto** [`BattleJoinService.join`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/engine/BattleJoinService.java) to correct side |
| Slots | Faction slots from participant military (unchanged) |
| Side restriction | Join allowed only for factions on that war side with a slot (unchanged 61b.04) |

### Signup (player opt-in)

| Rule | Detail |
|------|--------|
| **No auto-fighters** | War leader and all members **must** join the warband to fight; being online at create time does **not** add anyone |
| **Shell members** | **Zero** real players at create; no placeholder leader in `memberIds` |
| **Leader id sentinel** | Use deterministic placeholder UUID until first signup: `UUID.nameUUIDFromBytes(("warband_pending:" + warbandId).getBytes())` |
| **First signup** | First real player to join becomes warband leader (`setLeader`) |
| **War leader signup** | When the **war-side main faction leader** joins, they **become** warband leader (replace prior leader if any) |
| **War leader absent** | Any eligible member may lead the warband for battle purposes; warband leader is cosmetic for campaign auto flow |
| **Open join** | Faction warband `locked=true` but campaign path stays **open** to eligible war-side members (no invite list) |

### Devmode phantoms (61b compat)

| Rule | Detail |
|------|--------|
| **When** | Seed phantoms on **first real player signup**, not at empty shell create |
| **Cap** | Same formula: `min(phantom_count, max(0, previewSideLivesCap - 1))` after leader joins |
| **Lives / capture** | Unchanged 61b: phantoms count roster cap, not `playersAtStart` or capture presence |

### Messaging

| Location | Message intent |
|----------|----------------|
| Campaign battle ready broadcast | `/warband list` → join your faction warband (not `/battle join`) |
| Muster title | Point to warband list / join for signup |
| Battle join command on campaign | Reject or redirect: "Use /warband list to sign up" (campaign battles auto-enroll warbands) |

### Battle start edge cases

| Case | Rule |
|------|------|
| Zero signups on a side | Battle may still start (dev / autoresolve); side has 0 `playersAtStart`, lives formula uses 0 online |
| Solo test | Operator signs up once; devmode phantoms inflate roster cap only |

---

## Implementation notes (61c.04)

Locked constraints for code batches; no open design questions.

| Item | Rule |
|------|------|
| **`Warband.pendingLeaderUuid(warbandId)`** | `UUID.nameUUIDFromBytes(("warband_pending:" + warbandId).getBytes())`; add `isPendingLeader()` on [`Warband`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/warband/Warband.java) |
| **Campaign constructor** | No real players in `memberIds` at create; no muster title/sound in ctor; battle-ready broadcast only (61c.04) |
| **`CampaignBattleRosterService.enrollParticipant`** | Replace `BattleManager.getBattleByMemberId(leaderId)` skip with **band already on this battle side**; remove `BattleDevMode.seedPhantomsIfEnabled` at shell create |
| **Signup hook** | Centralize in warband join path ([`WarbandManager`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/warband/WarbandManager.java) GUI + `/warband join`): promote leader, war-leader override, phantom seed **once** per warband |
| **War leader identity** | Player name equals `Participant.getLeader().getLeader()` for the shell's main faction |
| **Faction resolve** | [`CampaignBattleJoinService.resolveFactionForWarband`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/campaign/CampaignBattleJoinService.java) already uses `warband.getId()` for faction warbands - safe with pending leader; do not resolve faction via pending sentinel |

---

## 61b supersession

Historical [61b.01](../step-61b/01-planning-lock.md) rules overridden for **campaign** warbands only:

| 61b.01 rule | 61c override |
|-------------|--------------|
| Campaign phantoms at warband create | First real signup only |
| Leader always real online UUID at create | Pending sentinel until signup |
| 61b solo checklist (`/warband create`, `/battle join`) | Superseded by [61c.05](./05-docs-verify.md) E2E |

Manual `/warband create` devmode rules in 61b.01 **unchanged**.

---

## Locked — docs & verify (61c.05 preview)

Replace [61b.05](../step-61b/05-docs-verify.md) solo checklist with **full campaign E2E**:

1. Declare war  
2. `warschedule` dev path (formatted output only)  
3. Campaign battle exists; warbands on sides; **no** auto member  
4. Staff: `/battle edit` spawns + capture points  
5. Players sign up via `/warband list`  
6. Battle start → lives, fight, capture, casualties  
7. Post-battle → `VOTING`, commitments updated  
8. War end probe: `/faction endwar` or white peace GUI (note: goal auto-apply is **62**, not 61c)  

Update [`Wars.md`](../../../../simplefactions/Documentation/Wars.md) staff-light row: templates = rules; staff set battle geometry per province battle.

---

## Locked — out of scope (61c)

- Step 62 surrender, objective retake, goal apply  
- Removing `/battle join` for staff manual battles  
- Persisting battle layout to province files (future)  
- Changing collective lives or casualty formulas  

---

## Verification (61c.01)

- [x] Lock aligned with [00-index](./00-index.md)  
- [x] No conflict with [61b.01](../step-61b/01-planning-lock.md) except phantom seed timing (updated above)  
- [x] [war-build-order.md](../../war-build-order.md) lists step 61c  

**Done when:** 61c.02–61c.05 can implement without open design questions.

**Done** (2026-08-21). **Next:** [61c.02 template settings-only](./02-template-settings-only.md).
