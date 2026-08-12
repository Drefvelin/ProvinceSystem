# Step 24 — Character sheet parity (traits, attrs, background)

**Repos:** `Workspace/rpcharacters` · `ProvinceSystem` · `frontend`  
**Depends on:** Step 22 sheet ([step-22](../step-22/00-index.md))  
**Playbook:** [14-character-creator.md](../../14-character-creator.md)

## Goal

Align `/character/[id]` with in-game Character Info: personality/evil traits only, merged attribute totals, profession EXP, writable-book background lore; fix empty trait lore blank lines in RPC; format birthday as `dd/mm/yyyy AE` without year padding.

## Locked rules

| Piece | Choice |
|-------|--------|
| Traits on sheet | Only keys in `Cache.editableTraits` (`personality`, `evil` from `editable-trait-types`) |
| Attributes | Totals from `character.getAttributeData()` after merge (race + all traits), not attribute-stage ranks alone |
| Profession EXP | Aggregated `getExperienceModifiers()` (alias + `%`), same as Character Traits item |
| Background | Writable-book text: lore of `background-trait-types` traits (`c.getDescription()`), separate from persona `description` |
| Empty lore | Omitting `description` in YAML is valid; never insert spacer/blank lines for empty lore (in-game book + web) |
| Birthday display | `dd/mm/yyyy AE` with zero-padded day/month, **never** pad year — e.g. `26/09/326 AE` |

## Suggested build order

1. **[01-rpc-sheet-fields](./01-rpc-sheet-fields.md)** — Empty lore + roster attributes/XP/traits/background  
2. **[02-ps-sheet-accept](./02-ps-sheet-accept.md)** — `sheet_json` accept + smoke + FE types  
3. **[03-sheet-ui](./03-sheet-ui.md)** — CharacterSheet birthday / EXP / background / attrs  
4. **[04-docs-verify](./04-docs-verify.md)** — Hubs + STAGING  

## Checkpoint

```text
empty lore → no blank book lines
  → roster: editable traits + merged attrs + profession EXP + background
  → /character/[id] matches Character Info (minus switch/kill)
  → birthday 26/09/326 AE
```

**Done when:** Sheet matches locked rules; empty lore does not pad the book; docs closed.

## Status

**24.01–24.04 done.** Operator [STAGING](../../../STAGING.md) Step 24 when ready; Phase 4 wardrobe as capacity allows.
