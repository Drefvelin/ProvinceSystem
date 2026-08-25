# Step 78.01 — Planning lock (battle installation picks)

**Plan + docs only.**  
**Authority for:** all 78.02–78.08 implementation batches.  
**Status:** done

**Gameplay docs (update in 78.08):** [`Wars.md`](../../../../simplefactions/Documentation/Wars.md) · [`Installations.md`](../../../../simplefactions/Documentation/Installations.md)

**Depends on:** [step 77](../step-77/01-planning-lock.md) (`VehicleCategoryRules`, berth registry), [step 59](../step-59/01-planning-lock.md) (vote close), [step 58](../step-58/01-planning-lock.md) (campaign GUI).

---

## Locked decisions (78.01)

| Decision | Value | Batch |
|----------|-------|-------|
| Who picks | **Faction leader only** | 78.04 |
| Pick scope | Own faction's **operational** installations only | 78.03 / 78.04 |
| Coalition | Each faction on a side picks **independently** (liege, vassal, ally) | 78.03 |
| Selection limit | **No cap** — any subset | 78.03 |
| Lock time | **`vote_close_hour`** (default 16 UTC), same event as hour vote close | 78.03 |
| Empty selection | **Nothing in play** for that faction | 78.03 |
| Reset | Cleared when battle day advances / new voting opens | 78.03 |
| Pre-lock enemy view | **Hidden** | 78.05 |
| Post-lock enemy view | **Visible** — committed installation ids/names per enemy faction | 78.05 |
| Battle window | **21-24 CET** (UTC config; see below) | 78.02 |
| Raid window | **19-20 CET** (UTC config; raids ship in 71) | 78.02 / 78.07 |
| Vehicle rule | Berthable types at **committed** install or **active siege fort** (owner faction) | 78.06 / 78.10 |
| Raid targets | Only installations in enemy **committed set** for current battle day | 78.07 |

---

## Principles

1. **Commitment = exposure.** Selecting an installation puts it in play for your side **and** makes it a valid raid target for the enemy (after lock).
2. **Opt-in per battle for ports/airports.** Siege forts on the active campaign schedule slot are in play for the owning faction's berthed emplacements without a pick (78.10).
3. **Leader agency for coalitions.** Vassals choose whether their airport is in play; liege cannot force ally picks.
4. **GUI-first.** Campaign view installations button (march icon, same as faction hub slot 32 pattern).
5. **Lock with vote.** Installation picks are not a separate deadline; they freeze at `vote_close_hour`.
6. **No em dashes** in player-facing strings.
7. **Raids before main battle** on battle day: raid window (19-20 CET) precedes campaign battle window (21-24 CET).

---

## Daily timeline (battle day)

Config stores **UTC hours** (existing `war.battle_schedule` pattern). **CET intent** (UTC+1, standard time):

```text
[ defender_deadline … vote_close + INSTALL LOCK … raid_window … battle_window ]
         12 UTC              16 UTC                    18-19 UTC      20-23 UTC
      (13 CET)            (17 CET)                  (19-20 CET)    (21-24 CET)
```

| Phase | CET (intent) | UTC (shipped default) | Config key |
|-------|--------------|----------------------|------------|
| Vote + picks open | — | — | From declare / prior battle end |
| Defender choice deadline | 13:00 | 12 | `defender_choice_deadline_hour` |
| **Vote close + installation lock** | **17:00** | **16** | `vote_close_hour` |
| **Raid window** | **19:00-20:00** | **18-19** | `raid_window_start_hour`, `raid_window_end_hour` (new) |
| **Campaign battle window** | **21:00-24:00** | **20-23** | `window_start_hour`, `window_end_hour` (updated) |

**Validation:** `vote_close_hour` < `raid_window_start_hour` <= `raid_window_end_hour` < `window_start_hour` <= `window_end_hour` <= 24.

Dev servers may use compressed hours; production comments document CET mapping.

---

## Installation pick rules

### Who can edit

| Actor | Can pick |
|-------|----------|
| Faction **leader** of a belligerent faction on either side | Yes, own installations only |
| Faction members (non-leader) | No — read-only summary in campaign GUI optional |
| Staff | Admin override out of scope |

### What can be selected

- Operational installations (`InstallationHandler` — not pending construction).
- Owned by the picking faction (direct ownership).
- Kinds: **`port` and `airport` only** — forts are not pickable (siege forts enter play via campaign schedule; see 78.10).
- Must be in a province your **coalition side still controls** (see control rule below).
- Toggle multi-select; no maximum count.

### Territory control (78.09)

Province `P` is controlled by faction `F`'s war side iff:

1. `P` is **not** in the enemy occupation bulge for that side.
2. And (`P` is in **our** occupation bulge **or** de jure on our side via `BelligerentTerritory`).

Attacker-side: enemy occ = `occupiedByDefender`, our occ = `occupiedByAttacker`. Defender-side: lists swapped.

### Empty pick

If a faction locks with **zero** installations selected:

- No vehicles from that faction's installations count for battle eligibility (berthable categories).
- None of that faction's installations are raid targets for the enemy.
- Non-berthable personal vehicles (e.g. train) still follow step 77 rules.

### Reset

When `battleDay` advances or voting reopens for the next cycle, **clear all** `battleInstallationPicks` for that war. Leaders must select again.

---

## Visibility rules

| Viewer | Before `vote_close_hour` | After `vote_close_hour` |
|--------|--------------------------|-------------------------|
| Picking faction leader | Own picks (edit) | Own picks (read-only until next cycle) |
| Same-side other factions | Own picks only | Own picks only |
| Enemy faction | **Cannot see** enemy commits | **Can see** enemy per-faction committed lists |
| Campaign GUI | Show own pick count / status | Show locked badge + enemy intel panel |

No map pin export required in 78.

---

## Vehicle battle eligibility (78.06, 78.10)

From step 77 lock, implemented at campaign battle join/spawn:

```text
vehicle battle-eligible iff
  NOT VehicleCategoryRules.isBerthableType(vehicleTypeId)
  OR (
    registry.mode == INSTALLATION
    AND installationId IN inPlaySet(playerFaction)
  )
```

`inPlaySet(factionId)` = committed picks for current `battleDay` **OR** active schedule siege `fortInstallationId` owned by that faction.

---

## Raid target rules (78.07; launch in 71)

> **Campaign raids (step 71 shipped):** `CampaignRaidEligibilityService` targets any operational enemy port/airport/fort. The committed-pick rules below apply to **`RaidTargetService`** (78.07 API) only, not campaign raid launch.

During **raid window** on battle day, a raid may target installation `I` iff:

1. `I` is operational.
2. Owner faction `F` is an enemy belligerent.
3. `I` is in `battleInstallationPicks[F]` for the current `battleDay` (post-lock set).
4. Raid kind matches installation kind (naval → port, air → airport) per step 71 templates. Fort raids are **not** committed via picks; step **71** wires fort raid targets separately.

No limit on how many enemy installations can be raided if all were committed.

---

## Persistence (78.03)

**War JSON** (new fields):

```json
{
  "battleInstallationPicks": {
    "<factionId>": ["port-1", "airport-2"]
  },
  "battleInstallationPicksBattleDay": "2026-08-24"
}
```

| Field | Rule |
|-------|------|
| `battleInstallationPicks` | Map faction id → ordered set of installation ids |
| `battleInstallationPicksBattleDay` | UTC date this pick set applies to; must match `battleDay` when locked |

Clear picks when `battleDay` changes or war ends.

---

## Campaign GUI (78.04)

| Element | Detail |
|---------|--------|
| Entry | **Installations** button on campaign view — march icon (`MenuItemType.INSTALLATIONS`), same visual as faction hub slot 32 |
| Sub-view | List operational installations (reuse `InstallationView` list patterns); click toggles selected (enchant glint / lore) |
| Slots | TBD in 78.04 batch doc; prefer dedicated `SFGUI.CAMPAIGN_INSTALLATION_PICK_VIEW` |
| Back | Returns to campaign view |
| Lock state | Before vote close: editable; after: read-only with "Locked at vote close" lore |

---

## Chat messages (draft; finalize in 78.04)

| Situation | Message |
|-----------|---------|
| Not leader | `§cOnly your faction leader can select installations for this battle.` |
| Picks locked | `§cInstallation choices are locked until the next battle day.` |
| Toggle on | `§aCommitted <installation name> for this battle.` |
| Toggle off | `§7Uncommitted <installation name>.` |

No em dashes.

---

## Code touch map

| Batch | Main files |
|-------|------------|
| 78.02 | `config.yml`, `Cache`, `ConfigLoader`, `BattleWindowService`, new `RaidWindowService` |
| 78.03 | `War` / `WarData`, `WarMapper`, `BattleInstallationPickService` |
| 78.04 | `CampaignView`, `CampaignCreator`, `CampaignInstallationPickView`, `SFGUI`, `InventoryManager` |
| 78.05 | `CampaignCreator` intel items, `BattleInstallationPickService` read API |
| 78.06 | `vehicles/` eligibility helper, battle join or spawn hook |
| 78.07 | Raid target validator (71 consumes) |
| 78.09 | `BattleInstallationPickEligibility`, pick service + GUI filter |
| 78.10 | `BattleSiegeFortService`, `BattleInstallationInPlayService`, vehicle eligibility |
| 78.08 | `Wars.md`, `Installations.md`, tests |

---

## Out of scope (step 78)

- Full raid battle UI and templates (step **71**)
- Raid war type (step **67**)
- War map export of picks (step **68** optional)
- Forcing minimum one installation pick
- Auto-commit from `fortInstallationId` / `portInstallationId` on schedule slots (siege fort in-play: **78.10**)

---

## Verify (78.01)

- [x] [`00-index.md`](./00-index.md) and this file exist under `step-78/`
- [ ] Locked rules aligned with user decisions (vote close, empty = none, post-lock visibility, CET windows)
- [x] Step 71 index updated to depend on 78
