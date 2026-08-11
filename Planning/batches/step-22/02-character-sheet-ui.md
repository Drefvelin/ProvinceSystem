# Batch 22.02 — Character sheet UI + shared shell

**Plan + build:** Shared padding shell for all `/character` nested routes; read-only identity sheet on detail; display-name race/class; Kits remains a single CTA.

**Repos:** `ProvinceSystem/frontend`  
**Depends on:** [01](./01-sheet-roster-sync.md)

## Locked UX

| Piece | Choice |
|-------|--------|
| Shell | Reuse list/create rhythm: `main` (or wrapper) `mx-auto max-w-lg px-6 py-8` (or `max-w-xl` if attributes need room) on `[id]`, kits, kit detail, edit |
| Detail | One composition: brand-free character sheet — name (hero), status, identity strip, description, attributes, traits, clues; then **Kits** link for ALIVE |
| Race / class | Prefer `race_name` / `class_name` from API; else catalog resolve by id; else capitalize id (never show raw id when a name exists) |
| List row | Same display-name helper as detail for race |
| Clues | Read-only list (or collapsed count + expand); no tip copy about Discord |
| Out | Switch / kill; create-wizard changes; tip nudges |

## Plan

1. **Shared layout** — Prefer `app/character/[id]/layout.tsx` (and ensure top `/character` page already padded) so kits routes inherit margins. Avoid duplicating `px-6` on every page.
2. **Types** — Extend `CharacterListItem` in [`api.ts`](../../../../ProvinceSystem/frontend/lib/characters/api.ts) for sheet fields.
3. **Detail page** — Replace stub meta line with sections (one job each): Identity · Description · Attributes · Traits · Clues · Kits CTA.
4. **Helpers** — `displayRace(item, catalog?)`, `displayClass(item, catalog?)` shared with list.
5. **UI-dev** — Fixture sheet data rich enough to review layout without API.
6. **Formatting** — Match existing Fraunces / cream / mist character visual language; no card grid in the hero; no flush-to-edge content.

## Verify

- [x] Detail shows Human (or catalog name), not `human`
- [x] Description, age/birthday, attributes, traits, clues visible when synced
- [x] Kits / kit detail / edit have side padding like the list page
- [x] No switch/kill controls

## Status

**Implemented** (22.02). Next: [03-docs-verify](./03-docs-verify.md).

## Out of scope

Docs (03); roster field plumbing beyond what 01 shipped.
