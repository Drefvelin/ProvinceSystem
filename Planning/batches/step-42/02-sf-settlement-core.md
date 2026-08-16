# Step 42.02 — SF settlement core

**Repos:** `Workspace/simplefactions`  
**Depends on:** [01-planning-lock](./01-planning-lock.md) · [Settlements.md](../../../../Workspace/simplefactions/Documentation/Settlements.md)  
**Branch:** `dev`

## Goal

Ship the `settlement` domain on `Faction`: entity, per-faction handler, persistence, province index, and tick `validate()` — **no** commands or map export yet.

## Package layout (new — lowercase only)

```text
settlement/
  Settlement.java
  handler/
    Handler.java
```

## Build

| File | Action |
|------|--------|
| `settlement/Settlement.java` | Entity: `id`, `name`, `centerProvince`, `centerX`, `centerZ`, `provinces`; `contains`, `isCenter`, guarded `addProvince` / `removeProvince` |
| `settlement/handler/Handler.java` | `byId`, `provinceIndex`; `getByProvince`, `getById`, `getAll`; `rebuildIndex()`; `validate()`; package-private `register` / `dissolve` stubs for 42.03 |
| `Database/SettlementData.java` | **Add** — serialize fields + `provinces` list |
| `Database/FactionData.java` | **Add** `settlements: List<SettlementData>` |
| `Database/Database.java` | Load/save settlements on faction round-trip |
| `Objects/Faction.java` | Hold `Handler settlementHandler`; accessor; construct on faction create/load |
| `Objects/Faction.java` | `tick()` → `settlementHandler.validate()` at end |
| `Loaders/ConfigLoader.java` | `settlement-found-distance` → `Cache.settlementFoundDistance` (default `2`) |
| `Cache.java` | `settlementFoundDistance` field |

### Handler.validate() (this batch)

Per [Settlements.md](../../../../Workspace/simplefactions/Documentation/Settlements.md):

- Strip provinces not directly owned by faction.
- Dissolve if centre missing, unowned, or `provinces` empty.
- Rebuild `provinceIndex`.

`dissolve()` in this batch may only remove settlement from maps; **capital clearing** wired in 42.03.

## Verify

Manual (dev server):

- [ ] Faction JSON round-trip: add test `SettlementData` in a faction file, restart, handler loads settlements and index resolves `getByProvince`.
- [ ] `validate()` strips a province after admin removes it from faction list (temporary test hook OK).

No new commands in this batch.

## Out of scope

- `setcapital` / claim / loss hooks ([03](./03-sf-setcapital-territory.md))
- Map export ([05](./05-sf-map-export.md))
- Unit tests optional; prefer manual + integration in 42.08 if no SF test harness

## Status

**Done.**

## Next

[03-sf-setcapital-territory](./03-sf-setcapital-territory.md)
