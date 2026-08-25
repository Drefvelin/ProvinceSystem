# Step 78.05 — Post-lock enemy intel

**Depends on:** [78.04](./04-campaign-gui-picks.md)  
**Repo:** `simplefactions`  
**Status:** done (2026-08-24)

## Goal

Enemy factions see committed installations **only after** `vote_close_hour`; hidden before lock.

## Shipped

1. `BattleInstallationPickService.getVisibleEnemyPicks` — empty pre-lock; per-enemy-faction picks post-lock
2. `CampaignCreator.buildEnemyInstallationIntelLines` / `createEnemyInstallationIntelItem`
3. Campaign view slot 34 intel book for participating belligerents

## Tasks

1. ~~`BattleInstallationPickService.getVisibleEnemyPicks(war, viewerFactionId, now)`~~ — done
2. ~~Campaign GUI intel panel (book or lore items) showing enemy commits post-lock~~ — done
3. ~~Same-side coalitions: still only own picks visible (not ally picks unless same faction)~~ — done
4. ~~Tests: pre-lock returns empty for enemy; post-lock returns committed ids; own picks always visible to own leader~~ — done

## Verify

```powershell
cd simplefactions; mvn test "-Dtest=BattleInstallationPickServiceTest"
cd simplefactions; mvn test
```
