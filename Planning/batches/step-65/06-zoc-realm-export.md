# Step 65.06 — War-aware fort ZOC export

**Repos:** `Workspace/simplefactions`  
**Depends on:** [65.01 planning lock](./01-planning-lock.md), [64.04 fort control](../step-64/04-fort-control.md)  
**Touches:** `ZocRealm`, `Markers`, `FortControlService` or war lookup helper, `Installations.md`

## Goal

`map_markers.json` `forts[].zoc_provinces` reflects **war-time fort controller** when the fort is part of an active campaign war.

## Scope

### Export logic

When building each fort row in `Markers.export`:

1. Resolve active war(s) referencing this fort (via campaign schedule, axis, or `fortControllers` key).
2. If `fortControllers[fortId]` present → use coalition's representative faction for `computeZocProvinces(controllerFaction, fortProvince)`.
3. Else → installation owner (current behavior).

**ZOC shape** unchanged (fort tile + same-top-realm land neighbours).

### Helper

```text
ZocRealm.resolveControllerFaction(installation, activeWars) -> Faction
```

Or thread `War` into export from a single "primary" active war per fort (document tie-break).

### Docs

- `Installations.md`: war-aware export **shipped** (remove "ships step 65" future tense).
- `ZocRealm` class javadoc: replace TODO step-43-war with implemented behavior.

## Tasks

1. War lookup for fort at export time.
2. Controller-aware `zoc_provinces` in `Markers`.
3. Unit tests for `ZocRealm` / export helper with mocked war + flipped controller.
4. `Installations.md` export section update (preview for 65.07).

## Out of scope

- Port pins / naval ZOC on map (ports have no ZOC)
- ProvinceSystem frontend changes (consumes same JSON shape)

## Done when

Export test: fort with `fortControllers` defender flip → ZOC provinces computed from controller faction's realm, not installation owner.
