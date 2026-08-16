# Step 42.04 — SF guild relocate

**Repos:** `Workspace/simplefactions`  
**Depends on:** [03-sf-setcapital-territory](./03-sf-setcapital-territory.md)  
**Spec:** [Settlements.md](../../../../Workspace/simplefactions/Documentation/Settlements.md) — Guild relocate

## Goal

When a guild **relocates** to another faction, apply settlement rules at the destination and **disband** the old settlement if no guild capitals remain in its provinces.

## Build

| File | Action |
|------|--------|
| `Guild/Guild.java` | `relocate(Faction f, int newCapital)` — after capital change, call settlement handler on old + new faction |
| `settlement/handler/Handler.java` | `onGuildRelocateFrom(Guild g, int oldCapital)` — if no guild in faction has capital in old settlement → dissolve |
| `settlement/handler/Handler.java` | `onGuildRelocateTo(Guild g, int newCapital, String nameIfNeeded)` — same as setcapital resolve at destination |
| `Managers/FactionManager.java` | Relocation accept flow — pass settlement **name** when destination requires founding (≥2 hops, no existing city) |

### Rules (locked)

**Old faction**

1. `S` = settlement containing guild’s old capital (if any).
2. After capital moves, if no guild has `capital ∈ S.provinces` → `dissolve(S)`.

**New faction**

- Reuse `resolveCapital` from 42.03 at `newCapital`.
- If founding required, relocation UI/flow must collect city name (extend relocation request object if needed).

No rename command.

## Verify

| Check | Expected |
|-------|----------|
| Last guild with capital in city relocates away | Old settlement disbanded |
| Other guilds still have capital in city | Settlement survives |
| Relocate to province in existing city on new faction | Join + capital set |
| Relocate to empty area ≥2 hops on new faction | Prompt/require name; new settlement |

## Out of scope

- Map export ([05](./05-sf-map-export.md))

## Status

**Done** (2026-08-15). Cross-faction and intra-faction GUI relocate wired to settlement handler; founding name via chat prompt.

## Next

[05-sf-map-export](./05-sf-map-export.md)
