# Batch 3.01 — Shell and hub

**Plan + build:** Shared site shell + hub landing; map becomes a module, not the homepage.

## Plan

1. Add `components/shell/SiteHeader.tsx` (or equivalent): brand mark/name + nav links **Home**, **Map** (`/map/main`), **Skins** (`/skins`). No R3B1RTH link.
2. Wire header into [`app/layout.tsx`](../../../frontend/app/layout.tsx); update metadata title/description to TFMC site (not “Map Viewer” only).
3. Replace [`app/page.tsx`](../../../frontend/app/page.tsx) redirect with a **hub** first viewport:
   - Brand-first composition (product name dominant)
   - One short supporting line
   - CTA group: Map + Skins (and optional Discord/Patreon later)
   - Atmosphere (gradient/texture) — follow site frontend design rules; avoid generic purple/Inter-default look
4. Ensure `/map/main` still loads; `/map/r3b1rth` remains reachable by URL only (do not add to hub or nav).
5. Stub `/skins` page (“Redeem coming next” or empty shell) so the nav link is not 404.

## Build

| File | Action |
|------|--------|
| `frontend/app/layout.tsx` | shell + metadata |
| `frontend/app/page.tsx` | hub |
| `frontend/app/skins/page.tsx` | stub |
| `frontend/components/shell/*` | create |
| CSS / fonts as needed | expressive fonts; CSS variables |

## Verify

- [ ] `npm run dev` → open `/` — hub, not map redirect  
- [ ] Nav Map → `/map/main` works  
- [ ] Nav Skins → `/skins` stub  
- [ ] No UI control links to `/map/r3b1rth`; typing URL still works  

## Out of scope

Skins redeem/upload, map hover/overlay polish, Discord links required.
