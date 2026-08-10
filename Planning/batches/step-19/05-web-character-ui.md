# Batch 19.05 — Web `/character` UI

**Plan + build:** Character nav tab, redeem (Remember me + logout), creation wizard from catalog, my characters (alive + dead). Visual quality bar = skins submission form.

**Repos:** `ProvinceSystem/frontend`

**Depends on:** [02](./02-creation-catalog-sync.md)–[04](./04-character-ingest.md) APIs live

## Plan

1. **Nav** — **Character** beside Map and Skins (`SiteHeader` + hub).
2. **Routes** — `/character` (list / redeem gate); `/character/create` (wizard).
3. **Redeem** — paste code; Remember me checkbox; store session (sessionStorage vs localStorage); show expiry; **Log out**.
4. **Wizard** — step through synced stages; attribute sheet UI matching formula; summary; submit create.
5. **List** — Alive · Pending · Dead; empty CTA; create disabled when no free slot.
6. **Design** — one composition per step; brand/atmosphere consistent with site; motion via `char-rise` / `char-step`.

## Verify

- [x] Tab visible; redeem → list *(UI wired)*  
- [x] Remember me uses localStorage; without it, sessionStorage  
- [x] Logout clears and calls `POST /characters/logout`  
- [x] Wizard enforces 12-point sheet client-side (Next disabled until exact spend); server still validates  
- [x] Dead / pending sections in list  
- [ ] Mobile usable *(layout is single-column; operator smoke on device)*  

## Implemented

- `lib/characters/{session,api,pointBuy,wizardState}.ts`
- `app/character/page.tsx`, `app/character/create/page.tsx`
- Components: `CharacterRedeemForm`, `CharacterList`, `CreationWizard`, `AttributeSheet`
- Nav + hub Character CTA

## Out of scope

Knife UI; player skin upload; in-game GUI parity pixel-perfect.
