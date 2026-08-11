# Batch 22.01 — Sheet fields on roster sync

**Plan + build:** Push the character identity fields the website needs for a read-only sheet. ProvinceSystem accepts, stores, and returns them on list (and detail if split).

**Repos:** `Workspace/rpcharacters` · `ProvinceSystem` backend  
**Depends on:** Existing roster sync ([RosterSyncService](../../../../Workspace/rpcharacters/src/main/java/net/tfminecraft/RPCharacters/ingest/RosterSyncService.java))

## Locked payload (per character in roster push)

Keep existing `id`, `name`, `status`, `race`, `class`, kit fields. Add:

| Field | Source (RPC) | Notes |
|-------|----------------|-------|
| `race_name` | `Race.getName()` stripped | Display; keep `race` as id |
| `class_name` | MMOCore `PlayerClass.getName()` when available | Fallback to class id |
| `age` | `PersonaService.resolveAge(character)` | String or int as already resolved in-game |
| `birthday` | `getBirthday()` | Fantasy YYYY-MM-DD if set |
| `gender` | `getGender()` | May be empty |
| `description` | `getPersonaDescription()` | Prose |
| `attributes` | Attribute ranks map (same keys as catalog point-buy) | From attribute traits / point service |
| `traits` | `[{ id, name, key }]` | Non-injury selection traits; names stripped |
| `clues` | Player clue strings | Read-only on web; count derived on FE |

Do not sync switch/kill state. Name colour stops stay player-level if already present.

## Plan

1. **RPC** — Extend `RosterSyncService` character JSON with the fields above (fail-soft if MMOCore/class missing).
2. **Attribute ranks** — Prefer existing hydration used by summary (`str1`/`str2`… → ranks); same map shape as create body `attributes`.
3. **PS** — `replace_roster` / `list_roster`: accept optional fields; store as JSON column(s) on `character_roster` (e.g. `sheet_json`) **or** discrete nullable columns if already patterned that way. Prefer one `sheet_json` TEXT for age/birthday/gender/description/attributes/traits/clues/race_name/class_name to avoid many migrations.
4. **List API** — Echo sheet fields on each character in `GET /characters` so detail can use list payload without a new endpoint (unless a dedicated `GET /characters/{id}` is cleaner; default: **enrich list rows**).
5. **Smoke** — Roster PUT with sheet fields → list returns them.

## Verify

- [x] After roster push, list character includes `race_name`, `description`, `attributes`, `traits`, `clues`
- [x] Legacy clients ignoring new fields still work
- [x] Empty gender/birthday omitted or null, not wrong defaults

## Status

**Implemented** (22.01). Next: [02-character-sheet-ui](./02-character-sheet-ui.md).

## Out of scope

FE sheet layout (02); docs close (03).
