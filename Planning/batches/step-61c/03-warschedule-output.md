# Step 61c.03 — Warschedule formatted output

**Repo:** SF · [00-index](./00-index.md) · **Depends on:** [61c.01 planning lock](./01-planning-lock.md) · **Next:** [61c.05 docs verify](./05-docs-verify.md)

## Goal

`/faction warschedule` subcommands print **short human-readable status** for what changed. Reserve full JSON dump for `/faction warstatus` only.

## New component

### `WarScheduleFeedbackFormatter` (recommended)

Path: `simplefactions/.../War/schedule/WarScheduleFeedbackFormatter.java`

```java
public final class WarScheduleFeedbackFormatter {
    public static List<String> format(String subcommand, War war) { ... }
}
```

| Input | Output lines (examples) |
|-------|-------------------------|
| `opencvote` | `Phase: VOTING · Battle day: 3` |
| `closevote` | `Scheduled: 2026-08-21T19:00:00Z · Province: 20 · Phase: SCHEDULED` |
| `castvote` | `Hour 21 · +4 selections · 2 voters · Phase: VOTING` |
| `skipday` | `Battle day: 4` |
| `forcequorum` | `Next close bypasses quorum` |
| `setscheduled` | `Scheduled: … · Province: 20 · Phase: SCHEDULED` |

Use [`BattleManager.getByWarId`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/engine/BattleManager.java) for optional `Campaign battle: campaign_w1_p20` line.

Formatting: prefix `§7` for labels, `§e` for values; no em dashes.

## Integration

| Location | Change |
|----------|--------|
| [`CommandManager`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/Managers/CommandManager.java) warschedule block | On success: `§a` + result.message(), then `format(subcommand, w)` lines; **remove** `WarDebugFormatter.formatStatusLines` |
| [`CommandManager`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/Managers/CommandManager.java) warstatus block | Unchanged (full JSON) |

Optional: enrich [`WarScheduleAdminService`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/schedule/WarScheduleAdminService.java) ok messages to avoid duplication with formatter (prefer single source in formatter).

## Tests

`WarScheduleFeedbackFormatterTest`:

| Test | Assert |
|------|--------|
| `closevote_scheduled_showsProvinceAndInstant` | Lines contain province id and ISO instant |
| `castvote_showsVoterCount` | Distinct voters reflected |
| `opencvote_showsPhase` | VOTING |
| `noJsonBraces` | Output lines do not contain `{` |

Extend [`WarScheduleAdminServiceTest`](../../../../simplefactions/src/test/java/me/Plugins/SimpleFactions/War/schedule/WarScheduleAdminServiceTest.java) only if service messages change.

## Verification

- [x] Each warschedule subcommand shows ≤ 3 formatted lines on success  
- [x] `warstatus` still dumps full JSON  
- [x] `mvn test` green  

**Done when:** warschedule success never calls `WarDebugFormatter.formatStatusLines`.

**Done** (2026-08-21). **Next:** [61c.04 campaign warband signup](./04-campaign-warband-signup.md).
