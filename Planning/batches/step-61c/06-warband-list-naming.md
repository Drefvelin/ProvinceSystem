# Step 61c.06 — Warband list fix & battle naming

**Repo:** SF · [00-index](./00-index.md) · **Depends on:** [61c.04 campaign warband signup](./04-campaign-warband-signup.md) · **Next:** [62 war end & goals](../step-62/00-index.md)

## Goal

Fix `/warband list` NPE on pending-leader campaign shells, and add display names separate from machine ids for battles and faction warbands.

## Changes

| Area | Detail |
|------|--------|
| **Warband leader display** | `getLeaderDisplayName()` returns `Pending signup` for empty shells; GUI/commands no longer call `getLeader().getName()` blindly |
| **Warband name** | Campaign shells: `The {FactionName} Host` |
| **Battle display name** | `Battle.displayName` separate from id; GUI shows name + id lore |
| **BattleNamingService** | Location priority: settlement > fort > county title > Wilderness; ordinals per war location key |
| **Persistence** | `War.locationBattleCounts` map serialized in war save |

## Naming rules

| Type | Pattern | Example |
|------|---------|---------|
| FIELD | `{Ordinal}Battle of {Location}` | `Second Battle of Lanbury` |
| SIEGE | `{Ordinal}Siege of {Location}` | `Siege of Fort Redoubt` |
| RAID | `{Location} Raid` | `Lanbury Raid` |

Ordinal increments when a campaign battle **completes** at that location key (not at shell create).

## Verification

- [x] `/warband list` safe on pending-leader shells
- [x] Campaign warband name `The {Faction} Host`
- [x] Battle list shows display name + id
- [x] `BattleNamingServiceTest`, `WarbandLeaderDisplayTest`
- [x] `mvn test` green

Manual:

- [ ] `/warband list` on test server: leader `Pending signup`, no crash
- [ ] Campaign broadcast uses battle display name
- [ ] Second fight at same settlement/county: `Second Battle of ...`

**Done** (2026-08-21). **Next:** [62 war end & goals](../step-62/00-index.md).
