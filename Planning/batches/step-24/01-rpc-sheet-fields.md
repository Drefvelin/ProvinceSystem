# Batch 24.01 — RPC empty lore + roster sheet fields

**Plan + build:** Fix blank lore lines in writable-book background; expand roster sheet payload for web parity.

**Repos:** `Workspace/rpcharacters`  
**Depends on:** Existing roster sync ([RosterSyncService](../../../../Workspace/rpcharacters/src/main/java/net/tfminecraft/RPCharacters/ingest/RosterSyncService.java))

## Locked

| Piece | Choice |
|-------|--------|
| Empty lore | Skip blank description lines on trait load; only append background lore when non-blank; spacer only between contributing traits |
| Attributes | `getAttributeData().getModifiers()` totals after `update()` |
| Experience | `getExperienceModifiers()` → `[{ profession, alias, amount }]` |
| Traits | Filter to `Cache.editableTraits` only |
| Background | Strip colour codes; join non-blank `getDescription()` with `\n`; omit if empty |
| Persona | Keep `description` as `getPersonaDescription()` |
| Birthday | ISO in payload; display on FE |

## Plan

1. **Trait.java** — Skip blank/`isBlank()` description lines when loading.
2. **RPCharacter.update()** — Only append background trait lore with content; separators only between contributing traits.
3. **RosterSyncService** — Call `update()` before serialize; replace attribute ranks with merged totals; add `experience_modifiers` + `background`; filter traits to editable keys.

## Verify

- [x] Trait with omitted/empty `description` adds no blank spacer to book
- [x] Roster traits are personality/evil only
- [x] Attributes include non–point-buy trait modifiers
- [x] `experience_modifiers` and `background` present when applicable

## Status

**Implemented** (24.01). Next: [02-ps-sheet-accept](./02-ps-sheet-accept.md).

## Out of scope

PS accept (02); FE sheet (03); docs close (04).
