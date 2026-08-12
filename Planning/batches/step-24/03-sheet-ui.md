# Batch 24.03 — Character sheet UI

**Plan + build:** Show birthday, merged attributes, personality/evil traits, profession EXP, and writable-book background.

**Repos:** `ProvinceSystem/frontend`  
**Depends on:** [02-ps-sheet-accept](./02-ps-sheet-accept.md)

## Locked

| Piece | Choice |
|-------|--------|
| Birthday | `formatFantasyBirthday` → `26/09/326 AE` (pad day/month, never pad year) |
| Attributes | Show synced totals (including zeros) |
| Traits | Personality / evil (sync-filtered); group by key |
| Profession EXP | Alias + signed `%` |
| Background | `whitespace-pre-wrap` from `background`; persona `description` separate |
| Empty | Omit empty sections |

## Plan

1. Update `CharacterSheet.tsx` sections as locked.
2. Update `sheetDev.ts` fixture with sample EXP + background.

## Verify

- [ ] Birthday not raw ISO
- [ ] Profession EXP and Background sections render when present
- [ ] Description (persona) and Background both visible when both set

## Status

**Implemented** (24.03). Next: [04-docs-verify](./04-docs-verify.md).

## Verify

- [x] Birthday not raw ISO
- [x] Profession EXP and Background sections render when present
- [x] Description (persona) and Background both visible when both set
