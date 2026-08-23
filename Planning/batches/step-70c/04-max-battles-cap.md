# Step 70c.04 — Max battles cap

**Repo:** SF  
**Depends on:** [70c.01](./01-planning-lock.md)

## Changes

- [Cache.java](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/Cache.java): `MAX_BATTLES_PER_LEG = 4`
- [ConfigLoader.java](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/Loaders/ConfigLoader.java): clamp + warn

## Done when

- [x] Values above 4 clamped at load
- [x] ConfigLoaderWarGoalsTest updated
