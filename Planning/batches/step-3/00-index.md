# Step 3 — Site shell + skins UI (batch index)

**Repo:** ProvinceSystem (frontend primarily; API already done on Step 2)  
**Branch:** continue `skins-api` (or cut `skins-ui` from it if you want a separate PR)  
**Depends on:** Step 2 smoke green — [`../step-2/08-verify-handoff.md`](../step-2/08-verify-handoff.md)

Parent design: [../../02-target-architecture.md](../../02-target-architecture.md), [../../05-skins-system.md](../../05-skins-system.md), [../../07-naming-conventions.md](../../07-naming-conventions.md).

## Goal

Turn the site from “map is the homepage” into a **server hub**: brand landing, public map, skins module — with R3B1RTH reachable only by direct URL (not linked in nav/hub).

Order locked earlier: **thin shell first → skins forms → handoff**. Map UX polish (realm card, crop) stays Track A / parallel, not required to finish Step 3.

## Scope

| In | Out |
|----|-----|
| Shared shell (nav, fonts, atmosphere) | Discord bot |
| Hub `/` (brand + CTAs to Map / Skins) | ArmourShop / IA write |
| `/map/main` in nav; `/map/r3b1rth` unlisted | 3D model viewer / review WebGL |
| `/skins` redeem → upload → status | Staff review UI (bot later) |
| Client size hints + slug UX | Changing skins API contracts |

## Batch order

1. [01-shell-and-hub](./01-shell-and-hub.md) — layout, hub, nav; stop redirect `/` → map  
2. [02-skins-redeem](./02-skins-redeem.md) — API client, redeem, session storage  
3. [03-skins-upload](./03-skins-upload.md) — kinds, slots, grip, slug, submit  
4. [04-skins-status-verify](./04-skins-status-verify.md) — status page + browser E2E checklist  

Do not start batch *N+1* until batch *N* is reviewable in the browser.

## Suggested layout

```text
frontend/app/
  layout.tsx                 Shell: SiteHeader + children
  page.tsx                   Hub (not redirect)
  map/[mapId]/page.tsx       Existing map (thin wrapper)
  skins/page.tsx             Redeem / upload / status flow
  components/
    shell/                   SiteHeader, maybe SiteFooter
    skins/                   RedeemForm, KindPicker, UploadForm, StatusCard
  lib/skins/                 api.ts, session.ts, sizes.ts, slug.ts
```

## Final checkpoint

```text
Open / → hub with TFMC brand + links to Map and Skins
Nav shows Map + Skins; no R3B1RTH link
/map/main works; /map/r3b1rth works if typed manually
/skins: redeem TEST-CODE-1 → upload armor or large_handheld → see pending status
```

Env: `NEXT_PUBLIC_API_URL=http://localhost:8000`. Never put staff/plugin keys in the frontend.
