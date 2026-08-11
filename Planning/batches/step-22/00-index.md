# Step 22 — Web character sheet (read-only parity)

**Repos:** `Workspace/rpcharacters` · `ProvinceSystem` · `frontend`  
**Depends on:** Step 21 kits UI ([step-21](../step-21/00-index.md)); Phase 1 create/list ([step-19](../step-19/00-index.md))  
**Playbook:** [14-character-creator.md](../../14-character-creator.md)

## Goal

Make `/character/[id]` a **read-only character sheet** that matches the in-game summary/menu identity view (name, race, class, age/birthday, gender, description, attributes, traits, clues), with clean layout and shared page margins on all character nested routes. Kits stay a nav action; switch/kill stay in-game only.

## Locked rules

| Piece | Choice |
|-------|--------|
| Scope | Visual / identity representation only |
| Out | Switch character; kill / permadeath; edit stages; tip nudges |
| Race / class | Show **display names** (catalog / MMOCore), not raw ids |
| Sheet fields | name, status, race, class, age, birthday, gender, description, attribute ranks, traits (by key groups), clues (read-only text) |
| Layout | Shared shell: `mx-auto max-w-lg px-6` (or `max-w-xl` if sheet needs width) on list + detail + kits + edit |
| Data | RPC roster push carries sheet fields; ProvinceSystem stores/echoes; FE resolves names via catalog when helpful |
| Name colours | Include if already on character and cheap to sync; otherwise omit until a later polish |

## Suggested build order

1. **[01-sheet-roster-sync](./01-sheet-roster-sync.md)** — Expand roster payload + PS accept/list  
2. **[02-character-sheet-ui](./02-character-sheet-ui.md)** — Shared shell + sheet + display-name race/class  
3. **[03-docs-verify](./03-docs-verify.md)** — Hubs + STAGING  

## Checkpoint

```text
roster sync sheet fields → /character/[id] shows full identity sheet
  → race/class display names → shared margins on kits routes
```

**Done when:** Detail page shows the same identity info as the in-game summary (minus switch/kill); race is not a bare id; nested character pages have consistent side padding.

## Status

**22.01–22.03 done.** Operator [STAGING](../../../STAGING.md) Step 22 when ready; Phase 4 wardrobe as capacity allows.