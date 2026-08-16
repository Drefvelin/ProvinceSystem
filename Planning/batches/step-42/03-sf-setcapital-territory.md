# Step 42.03 — SF setcapital + territory

**Repos:** `Workspace/simplefactions`  
**Depends on:** [02-sf-settlement-core](./02-sf-settlement-core.md)  
**Spec:** [Settlements.md](../../../../Workspace/simplefactions/Documentation/Settlements.md)

## Goal

Full gameplay loop: found/join via `setcapital`, territory at create, claim growth, province loss, dissolve with capital cleanup, player messages, tab-complete settlement **ids**.

## Build

### Handler logic (`settlement/handler/Handler.java`)

| Method | Behaviour |
|--------|-----------|
| `resolveCapital(Player, int province, String nameOpt, boolean factionCapital)` | Full decision tree: in-settlement / join / found / reject |
| `found(name, province, x, z)` | Create settlement + initial province ring (land neighbours, directly owned, unclaimed) |
| `join(Settlement s, int province)` | Add `P` to `s.provinces` if missing; set capital |
| `dissolve(Settlement s)` | Clear all guild + faction capitals in `s.provinces`; remove settlement |
| `onProvinceClaimed(int p)` | Adjacent to settlement territory → add; random if multiple |
| `onProvinceLost(int p)` | Non-centre → remove; centre → dissolve |
| `minLandHops(int from, int toProvince)` | Province graph (non-water edges) |
| `getPopulation(Settlement s)` | Guilds with `capital ∈ s.provinces` |

**Join tie-break** when multiple centres are 1 hop away: lowest hop count, then stable settlement `id`.

**Faction rule:** capital on existing settlement only if `P == centerProvince`.

### Commands (`Managers/CommandManager.java`)

| Command | Change |
|---------|--------|
| `/faction setcapital [name]` | Optional name; delegate to handler |
| `/guild setcapital [name]` | Same |

Replace current “already has capital” one-shot flow where it conflicts with spec (document behaviour: moving capital may remain out of scope except via relocate).

### Province hooks (`Objects/Handler/ProvinceHandler.java`)

- After `addProvince` → `faction.getSettlementHandler().onProvinceClaimed(p)`
- After `removeProvince` / unclaim path → `onProvinceLost(p)`

### Tab completion (`Utils/TabCompletion.java`)

- Settlement **ids** for faction (when subcommand relevant)

### Player feedback

Messages for: founded (name + id), joined (settlement name), rejected (reason), dissolved (city name).

### Map enqueue

Call `FactionManager.getMap().enqueue(...)` when settlements found/dissolved/territory changes materially (match existing nation enqueue pattern).

## Verify (staging / dev)

| Check | Expected |
|-------|----------|
| `/guild setcapital "Rivendell"` on empty land ≥2 hops from any centre | New settlement; provinces = centre + eligible neighbours |
| `/guild setcapital` on province in existing city | Capital set; no new settlement |
| `/guild setcapital` 1 hop from centre, not in list | Joins city; `P` added to provinces |
| `/faction setcapital` on outer ring of city | Rejected |
| `/faction setcapital` on centre | Faction capital set |
| Claim province adjacent to one city | Added to that city |
| Claim province adjacent to two cities | Random assignment (run twice — can differ) |
| Unclaim non-centre province in city | Removed from list |
| Unclaim centre | Settlement dissolved; guild/faction capitals cleared |

## Out of scope

- Relocate ([04](./04-sf-relocate.md))
- Map export ([05](./05-sf-map-export.md))

## Status

**Done** (2026-08-15). Handler gameplay, commands, province hooks, tab-complete, messages.

## Next

[04-sf-relocate](./04-sf-relocate.md)
