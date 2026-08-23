# Step 61b.01 — Battle dev mode planning lock

**Repo:** SF · [00-index](./00-index.md) · **Blocks:** [61b.02](./02-capture-threshold.md)–[61b.05](./05-docs-verify.md)

> **Campaign warband / phantom timing superseded by [61c.01](../step-61c/01-planning-lock.md)** (signup-required shells, phantoms on first signup). Manual `/warband create` devmode rules below unchanged.

## Goal

Lock rules for solo test-server battle staging before code. No Java in this batch.

---

## Locked — `BattleDevMode` toggle

| Rule | Detail |
|------|--------|
| **Command** | `/battle devmode on`, `/battle devmode off`, `/battle devmode status` |
| **Permission** | Admin only (same gate as other `/battle` staff commands via [`BattlePermissions`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/util/BattlePermissions.java)) |
| **Persistence** | **None.** Static in-memory flag only; **off** after plugin disable/restart |
| **Scope** | Affects warband creation seeding and campaign join validation only; does not change war FSM or commitment math |

---

## Locked — phantom warband members

Warband members are **UUIDs**, not faction-style name strings. Phantoms use deterministic IDs:

```text
UUID.nameUUIDFromBytes(("battle_phantom:" + warbandId + ":" + index).getBytes())
```

| Rule | Detail |
|------|--------|
| **When** | Only if `BattleDevMode.isEnabled()` at warband create time |
| **Count** | **10** phantoms per new warband (config key optional in 61b.03: `battle.devmode.phantom_count`, default 10) |
| **Cap-aware seed** | `phantomsAdded = min(phantom_count, max(0, previewSideLivesCap - 1))` for campaign warbands so leader + phantoms never exceeds lives cap |
| **Manual warband** | [`/warband create`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/ui/BattleCommandManager.java): leader + 10 phantoms |
| **Campaign warband** | [`Warband(War, Participant, offense)`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/warband/Warband.java): after real leader UUID, add 10 phantoms |
| **Leader** | Always a **real** online player UUID; phantoms never become leader |
| **Online** | Phantoms are **never** online `Player` entities |

### What phantoms count for

| System | Count phantoms? |
|--------|-----------------|
| `Warband.getMemberCount()` / roster size | **Yes** |
| Campaign side roster cap vs collective lives | **Yes** (total member IDs on all warbands on that battle side) |
| `BattleLivesService.countPlayersAtStart` | **No** - online humans only |
| Capture point presence (`CapturePoint.updateSides`) | **No** - only real players at zone |
| Casualty ledger (61.05) | **No** - real deaths/disconnects only |
| Boss bar / battle participant lists | **No** - `getPlayers()` stays online-only unless explicitly changed |

Rationale: phantoms inflate roster for UI/slot testing without breaking the 61 lives formula or inventing fake deaths.

---

## Locked — capture point minimum (prod + dev)

| Rule | Detail |
|------|--------|
| **Replace** | Hardcoded `>= 3` in [`CapturePoint.updateSides`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/engine/CapturePoint.java) |
| **Config** | `battle.capture_min_players` default **1** in [`config.yml`](../../../../simplefactions/src/main/resources/config.yml) |
| **Prod intent** | **1** for linear/sequential capture (locked product decision in 61b) |
| **Devmode** | Does not override; config applies everywhere |

---

## Locked — campaign battle join rules

Applies when `battle.getWarId() != null` and battle not started.

### Side membership

Player must belong to a faction on the **target battle side** (attacker or defender war side):

- Resolve player faction via `FactionManager.getByMember(playerName)`
- Resolve war side via `war.getSide(faction)` and map to `BattleTemplate.ATTACKER_SIDE` / `DEFENDER_SIDE`
- Reject join if faction side does not match requested `sideId`

Staff manual battles (`warId == null`): unchanged (no side check).

### Roster cap = side collective lives

After [`BattleLivesService.applyCampaignLives`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/military/BattleLivesService.java) at `battle.start()`, each `BattleSide` has `maxLives` set.

| Rule | Detail |
|------|--------|
| **Cap** | Sum of `warband.getMemberCount()` across all warbands on that side **must not exceed** `side.getMaxLives()` (or current lives at join time if before start: use template lives until start applies - see 61b.04) |
| **Before start** | At join time pre-start: use **computed preview** lives from `BattleLivesService.computeSideLives` with current online roster on that side (same as start will apply) as cap |
| **Reject message** | Player-facing: side roster full for this battle |

### Faction warband slots (campaign only)

For `warband.isFaction() && battle.warId != null`:

| Rule | Detail |
|------|--------|
| **Bypass** | Do not use `WarbandSlot.isFull()` / per-faction manpower caps for join/rejoin |
| **Use instead** | Side-level roster cap above |
| **Manual / non-campaign warbands** | Keep existing slot + invite rules |

---

## Locked — out of scope (61b)

- Auto-seed defender warband with phantoms for solo two-sided fights
- Phantom players standing on capture points
- Changing collective lives formula
- Warband roster using commit snapshot (separate backlog in 61 index)
- Raid-specific join rules (66)

---

## Verification (61b.01)

- [ ] Lock doc aligned with [00-index](./00-index.md)
- [ ] [DEV-SHORTCUTS.md](../../DEV-SHORTCUTS.md) section stub added (filled in 61b.05)
- [ ] No conflict with [61.01 planning lock](../step-61/01-planning-lock.md) casualty/lives rules

**Done when:** 61b.02–61b.05 can implement without open design questions.
