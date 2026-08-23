# Step 61.01 — Planning lock (military & casualties)

**Done** (2026-08-20). **Plan + docs only.** Lock collective lives, battle pool rules, militia deployment, levy commit, casualty order, and step 61 boundaries before 61.02+ code.

**Repos:** `Workspace/simplefactions`  
**Depends on:** [00-index](./00-index.md) · [step-60.09](../step-60/09-schedule-hook.md) · [Wars.md](../../../../simplefactions/Documentation/Wars.md) · [war-build-order.md](../../war-build-order.md)  
**Authoritative gameplay doc:** [Wars.md](../../../../simplefactions/Documentation/Wars.md)

## Goal

Lock step 61 boundaries so batches 61.02–61.07 do not creep into goal apply (62), fort ZOC siege pick (63), naval routing (64), inter-battle raids (65), raid war declare (66), map export (67), or declare codes (68).

**61.01 itself:** lock doc + Wars.md alignment only. **No Java changes.**

---

## Locked — step 61 scope

| In scope | Out of scope |
|----------|----------------|
| **War commitment snapshot** at declare (`WarCommitment.count` filled) | Goal apply / reparations (62) |
| **Levy pool frozen** per subject for war duration | Fort ZOC → siege mode pick (63) |
| **Battle pool resolver** (offense/defense by battle province + phase) | Naval campaign routing / port pick (64) |
| **Militia rules** (own land, vassal/overlord split) | Inter-battle tactical raids (65) |
| **Collective lives** from committed regiments (campaign field/siege) | Raid **war type** one-battle flow (66) |
| **Casualty ledger** (deaths + disconnects in campaign battles) | Map export payload (67) |
| **Regiment casualty apply** after campaign battle end | Declare codes (68) |
| Wire into **60.09** outcome hook (`CampaignBattleOutcomeService`) | Staff manual battles (`warId == null`) |

---

## Locked — war commitment (minimal rules)

Four rules cover the whole military pool:

| # | Rule |
|---|------|
| **1** | **Fighter OR levy-only, never both.** On a war side, a faction is either a **fighter** (main, auto-called subject, or accepted ally) or **levy-only** (not fighting on that side). Levy-only troops roll up to their **direct overlord on that side** if that overlord is a fighter. |
| **2** | **Fighter own regiments are live.** Militia/professional slots are read at **each battle start** (buildup during war counts). |
| **3** | **Levy is frozen.** Levy rows are snapshotted at fixed moments only; subject slot growth and levy % changes do **not** add mid-war levy. |
| **4** | **Every levy row names who loses.** Row shape: `holder → source → count`. Casualties debit **source**, not holder twice. |

### Levy snapshot moments (only ways to add levy rows)

| Moment | What gets snapshotted |
|--------|------------------------|
| **War declare** | Levy from levy-only subjects under each **fighter** on that side (walk `getLevies()`; skip any source in the side's fighter set) |
| **Ally join** | Same levy snapshot for the **joining ally** only (new levy rows allowed here) |

### Levy mid-war changes

| Event | Levy rows |
|-------|-----------|
| Subject builds more troops / levy % changes | **No change** |
| Someone **becomes** a new vassal (of main **or** ally) | **Do not add** |
| Someone **stops** being a vassal | **Remove** rows where that faction is `sourceFactionId` **or any descendant in its subject subtree**; if a **fighter** leaves the side, remove all rows where it is `holderFactionId` |

Full algorithm, examples, and anti-double-count rules: [61.01b levy & vassal lock](./01b-levy-vassal-lock.md).

---

## Locked — war commitment (`WarCommitment`)

**Levy holder/source, nested vassal chains, and vassal-break cascade:** [61.01b levy & vassal lock](./01b-levy-vassal-lock.md).

Step **56.07** shipped the record + stub `commitForWar` (count **0**). Step **61** fills real counts.

| Field | Rule |
|-------|------|
| `warId` | Active war id |
| `factionId` | **Holder** faction (fighter whose pool includes this row) |
| `regimentId` | Regiment type id (`militia`, `professional`, `levy`, … from `regiments.yml`) |
| `sourceFactionId` | **Levy only:** faction that loses slots/casualties. **Own regiments:** same as `factionId` (or null = self) |
| `count` | **Levy:** frozen integer at snapshot. **Own regiments:** casualties remaining tracker (decremented on apply); battle pool reads **live** `currentSlots` |
| `committedAt` | Snapshot timestamp |

### When to commit

| Trigger | Action |
|---------|--------|
| `WarManager.declareWar` | Commit all fighters on both sides + levy snapshot per fighter |
| Subject auto-included on declare | Fighter commit + levy snapshot under that subject if it has levy-only sub-vassals |
| Call-to-arms accept | Fighter commit for joiner + **levy snapshot for joiner** (only mid-war levy add) |
| Vassal relation broken mid-war | Drop levy rows for broken subject **subtree**; drop holder rows if fighter leaves side (61.01b) |
| Re-commit own regiments | **Forbidden** per `(warId, factionId, regimentId)` baseline row |
| Re-snapshot levy | **Forbidden** except ally-join trigger and vassal-break removal |

### Levy rows

| Rule | Detail |
|------|--------|
| Source data | Nearest-fighter holder walk (61.01b); **not** independent `getLevies()` per fighter |
| Granularity | One row per `(holderFactionId, sourceFactionId, levy)` |
| Mid-war buildup | **Ignored** — no new rows from buildup or new vassalage |
| Losses | Decrement row `count`; decrement source faction military / `sentToOverlord` tallies |

Non-levy regiments: one row per `(factionId, regimentId)` at first commit. Battle pool and lives use **live** fighter slots (rule 2). Commitment row tracks war-scoped casualty debits (61.06).

---

## Locked — battle pool (offense vs defense)

Pool selection depends on **where the battle is fought**, not who declared war. Use `scheduledBattleProvinceId` / `battle.provinceId` + province owner lookup.

### Phase → who is "offensive" in the fight

Use existing `CampaignProgressionService.getOffensiveSide(war)`:

| `CampaignPhase` | Offensive belligerent role |
|-----------------|----------------------------|
| `INVASION` | Attacker |
| `RETAKE`, `COUNTER_PUSH` | Defender |

### Regiment offense flag filter

For each faction on a battle side, sum committed regiments where `Regiment.isOffensive()` matches the side's **pool mode**:

| Battle context | Attacker-side factions use | Defender-side factions use |
|----------------|----------------------------|----------------------------|
| Offensive side fighting **toward** objective (normal invasion node on defender land) | **Offensive** regiments | **Defensive** regiments |
| Defensive side **counter-pushing** on attacker land | **Defensive** regiments | **Offensive** regiments |

Implementation rule: derive `BelligerentRole offensiveRole = getOffensiveSide(war)`; battle side aligned with `offensiveRole` uses offensive regiments; the other side uses defensive regiments (`!isOffensive()` for professional army; militia/levy follow separate rules below).

---

## Locked — militia deployment

From [Wars.md § Militia](../../../../simplefactions/Documentation/Wars.md):

| Rule | Detail |
|------|--------|
| **Own land only** | Faction militia counts only if `TitleManager.getByProvince(battleProvinceId) == faction` |
| **Overlord in vassal land** | Overlord **militia excluded**; overlord sends professional army + levies only |
| **Battle in vassal land** | Vassal faction gets **full** military including militia; overlord gets non-militia + levies |

Militia regiment id: **`militia`** (`regiments.yml`). Militia is always treated as **defensive** pool (`offense: false` implicit — not in yaml but not `offense: true`).

---

## Locked — collective lives (campaign field + siege)

Replace template-default lives for **campaign** battles (`battle.warId != null`, types **FIELD** and **SIEGE**) at **`battle.start()`**.

### Formula (per side)

```text
committedRegiments = sum of eligible committed counts for that side's battle pool
playersAtStart     = online fighters on that side at start (unique UUIDs)
rawLives           = livesPerRegiment * committedRegiments - playersAtStart
sideLives          = max(minSideLives, rawLives)
```

| Constraint | Rule |
|------------|------|
| `max_players <= lives` | Clamp `playersAtStart` contribution so lives never below `minSideLives` if side has fighters |
| Life type | **Collective only** (campaign field/siege and staff manual) |
| Raids | **Unchanged** — template / raid defender modes from 60.08 |
| Staff battles | `warId == null` — template lives unchanged |

### Config defaults

| Key | Default |
|-----|---------|
| `war.battle_military.lives_per_regiment` | `5` |
| `war.battle_military.min_side_lives` | `1` |

---

## Locked — casualty ledger (during battle)

Track losses for campaign field/siege battles only.

| Event | Counts toward side casualties |
|-------|-------------------------------|
| Death in battle (life tick / jail) | **Yes** |
| Disconnect after start (field/siege) | **Yes** (same as raid attacker-out pattern) |
| Province-leave penalty death | **Yes** |
| Staff / raid battles | **No ledger** (61 scope) |

Store per battle: `{ sideId -> casualtyCount }` cleared on battle end.

---

## Locked — casualty apply (after battle)

Hook: **`CampaignBattleOutcomeService.handleBattleEnded`** — run **after** winner known (or zero winner), **before** `openVote`. Apply even when **no winner** (both sides take losses).

### Debit order (per side, per faction contributor)

1. **Militia** (if that faction's militia was eligible at battle province) — up to militia committed count  
2. **Army + levy** — remaining casualties split **proportionally** by committed count across contributors (fair split; not "vassals always first")

### What gets decremented

| Target | Rule |
|--------|------|
| `WarCommitment.count` | Primary war-scoped pool (used for future battle lives) |
| Faction military slots | Decrement `Regiment.currentSlots` (and levy sent counts) to match applied losses — **permanent until rebuilt** |

Levy losses decrement holder levy commitment row and **source** faction slots / `sentToOverlord` tallies consistently.

### No winner / white battle end

Still apply casualties from ledger counts; no occupation/progression change (already handled in 60.09).

---

## Locked — integration points

| Location | 61 change |
|----------|-----------|
| `WarManager.declareWar` | Full `commitForWar` snapshot (61.02) |
| `War.call` / ally accept path | Commit joiner faction |
| `CampaignBattleLaunchService` / `Battle.start()` | Apply collective lives from pool (61.04) |
| `BattleManager` death / quit / leave penalty | Feed casualty ledger (61.05) |
| `CampaignBattleOutcomeService` | `BattleCasualtyService.apply(war, battle, ledger)` (61.06) |
| `WarManager.persist` | Persist commitments when counts change (61.06) |

---

## Locked — batches (61.02–61.07)

| Batch | Summary |
|-------|---------|
| [61.02 war commitment](./02-war-commitment.md) | Real `commitForWar` snapshot + nearest-holder levy + relation hooks + tests |
| [61.03 battle pool](./03-battle-pool.md) | Offense/defense + militia eligibility by province |
| [61.04 collective lives](./04-collective-lives.md) | Lives formula at campaign battle start |
| [61.05 casualty ledger](./05-casualty-ledger.md) | Track deaths/disconnects per side |
| [61.06 casualty apply](./06-casualty-apply.md) | Regiment losses + outcome hook + persistence |
| [61.07 docs verify](./07-docs-verify.md) | End-to-end tests + staging checklist |

---

## Verification (61.01)

- [x] Commitment snapshot rules locked
- [x] Battle pool + militia rules locked
- [x] Collective lives formula locked
- [x] Casualty ledger + apply order locked
- [x] Step 61 scope vs 62-68 locked
- [x] Wars.md updated to match

**Done when:** this file + [00-index](./00-index.md) + [Wars.md](../../../../simplefactions/Documentation/Wars.md) aligned.
