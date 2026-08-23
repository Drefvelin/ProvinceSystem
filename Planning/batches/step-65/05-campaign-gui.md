# Step 65.05 — Campaign GUI naval battle kinds

**Repos:** `Workspace/simplefactions`  
**Depends on:** [65.02 slot model](./02-port-zoc-naval-slots.md), [64.07 GUI](../step-64/07-campaign-gui.md)  
**Touches:** `CampaignUiCopy`, `CampaignRouteRenderer`, `CampaignCreator`, `WarScheduleFeedbackFormatter`, `WarDebugFormatter`, tests

## Goal

Campaign route GUI shows **Naval Battle** and **Naval Invasion** on scheduled provinces (player-facing copy, no em dashes).

## Scope

### Lore labels

| `CampaignBattleKind` | Lore |
|----------------------|------|
| `FIELD` | `Field Battle` |
| `SIEGE` | `Siege` |
| `NAVAL` | `Naval Battle` |
| `NAVAL_INVASION` | `Naval Invasion` |

Extend `CampaignUiCopy.formatBattleKind`.

### Route rendering

- `CampaignRouteRenderer`: append kind lore for `NAVAL` / `NAVAL_INVASION` provinces (same hook as 64.07).
- `CampaignCreator`: distinct item material or enchant glint for naval kinds (e.g. trident vs field sword; siege keeps existing glint).

### Admin / debug

- `WarScheduleFeedbackFormatter`: kind + optional `portInstallationId` per slot.
- `WarDebugFormatter`: include `portInstallationId` in schedule JSON lines.

## Tasks

1. `CampaignUiCopy` naval strings.
2. Renderer + creator integration.
3. Admin formatters.
4. Tests in `CampaignRouteRendererTest`, `WarScheduleFeedbackFormatterTest`, `WarDebugFormatterTest`.

## Out of scope

- Map website battle markers (step 67)
- Installation pick UI (deferred)

## Done when

Campaign view on a war with naval schedule slots shows correct lore and distinguishable route items.
