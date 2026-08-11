# Batch 21.09 — Web character kits UI (not create wizard)

**Plan + build:** Sync all kits to the website. From `/character`, open an ALIVE character (menu-like detail), open Kits, open a kit, show all items, Edit only editable ones. Remove create-wizard knife step (21.07 path). Customise only while that kit is claimable for the character; once-per-character + already claimed → no edit.

**Repos:** `ProvinceSystem` · `frontend` · RPC catalog/kits sync from [08](./08-kits-yml-and-kit-service.md)  
**Depends on:** [08](./08-kits-yml-and-kit-service.md); lore customise/apply from 02–04  
**Supersedes:** [07-create-window-customise](./07-create-window-customise.md) wizard entry; list “Customise knife” CTA

## Locked

| Piece | Choice |
|-------|--------|
| Entry | `/character` → click ALIVE character → character screen → **Kits** → kit → **Edit** on editable item |
| Show | All kit items; non-editable visible but not editable |
| Editor | Existing lore-item editor patterns (NBT preview, pick/upload, name, lore) |
| Eligibility | Kit not yet claimed for this character when `once-per-character`; or always claimable window for repeatable kits before each claim (define: customise allowed when next claim is possible / not mid-pending) — **default:** customise allowed iff character can still claim that kit (once-per-char: not granted; repeatable: always until/unless you lock after pending — prefer: allow customise whenever kit status is claimable for next grant) |
| Claimed once-per-char | No Edit; show claimed state |
| Create wizard | **Remove** knife step from `CreationWizard`; create in-game or web without kits |
| Pending create | No longer key customise to create UUID for wizard; customise against real character id after create/ingest (in-game create + web create both fine) |
| Sync | Full kits list + editable flags + per-character per-kit status + per-kit cooldown remaining |
| Messaging | No tip nudges |

## Plan

1. **API** — Expose kits catalog (from RPC sync); list character kits + items; customise routes scoped by `character_id` + `kit_id` + `kit_key` (item key). Eligibility = claimable for that kit (not `granted` if once-per-character).
2. **Remount / pending-create** — Drop or stop using create-UUID customise path from 07; require roster character id.
3. **FE** — Character detail page/section (alive only); Kits list; kit detail with items; Edit → lore editor. Remove wizard knife step and create-id customise call.
4. **RPC sync** — Push all kits defs with creation catalog or dedicated kits PUT; roster includes per-kit statuses.
5. **Claim gate** — Keep plugin claim-status keyed by kit id (from 08).

## Status

**Implemented** (character → Kits → Edit; wizard knife removed; per-kit customise gate).

## Verify

- [x] Create character in-game → on web open character → Kits → starter → Edit knife → save *(routes + API)*
- [x] Create wizard has no knife step
- [x] Non-editable kit lines visible without Edit
- [x] After once-per-character claim, Edit disabled / customise 403
- [x] `pending_skin` blocks in-game claim for that kit *(08)*
- [x] All kits from `kits.yml` appear on site after sync *(catalog kits + GET /characters/kits)*

## Out of scope

21.05 docs; designing extra kits beyond `starter` content (schema must allow them).
