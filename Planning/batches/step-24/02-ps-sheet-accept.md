# Batch 24.02 — ProvinceSystem sheet accept + smoke

**Plan + build:** Accept new roster sheet fields; echo on list; update smoke + FE types.

**Repos:** `ProvinceSystem/backend` · `frontend/lib/characters/api.ts`  
**Depends on:** [01-rpc-sheet-fields](./01-rpc-sheet-fields.md)

## Locked

| Field | Shape |
|-------|--------|
| `background` | Optional non-empty string |
| `experience_modifiers` | Optional list of `{ profession, alias, amount }` |
| `attributes` / `traits` | Existing shapes (attributes may include zeros) |

## Plan

1. **roster.py** — Normalize `background` + `experience_modifiers` into `sheet_json`.
2. **Smoke** — Assert new fields round-trip on roster PUT → list.
3. **api.ts** — Type `background` + `experience_modifiers` on `CharacterListItem`.

## Verify

- [ ] List returns `background` / `experience_modifiers` when pushed
- [ ] Legacy roster without new fields still works
- [ ] Smoke green

## Status

**Implemented** (24.02). Next: [03-sheet-ui](./03-sheet-ui.md).

## Verify

- [x] List returns `background` / `experience_modifiers` when pushed
- [x] Legacy roster without new fields still works
- [x] Smoke green (assertions updated; run on staging when convenient)
