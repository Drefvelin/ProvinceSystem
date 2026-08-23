# Step 70c.02 — Geographic route sort

**Repo:** SF  
**Depends on:** [70c.01](./01-planning-lock.md)

## Changes

- [CampaignRouteRenderer.java](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/progression/CampaignRouteRenderer.java): merge both legs, sort by axis index; `isBorderFirstBattleSlot`
- Remove `Counter-push schedule` lore

## Done when

- [x] `buildRouteEntries` returns geographic order
- [x] Counter-push lore removed
