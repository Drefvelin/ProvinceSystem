# Step 3 — Skins UI (batch index)

**Repo:** ProvinceSystem frontend  
**Branch:** stay on `skins-api`, or open `skins-ui` from updated `skins-api` / `site-rework`  
**Depends on:** Step 2 complete ([../step-2/00-index.md](../step-2/00-index.md); smoke: `backend/scripts/skins_e2e_smoke.ps1`)

## Goal

Player-facing `/skins`: redeem code → choose kind → upload with exact-size guidance → see status. No Discord or ArmourShop required.

## First UI work (batches TBD)

1. Redeem form → `POST /skins/redeem`; store session token (memory / sessionStorage).
2. Kind picker: `armor_set` | `item` | `handheld` | `large_handheld`.
3. Upload form with labeled slots; **large_handheld** requires grip preset (`bottom` / `middle` / `top`).
4. Client-side size hints (icons 16×16, layers 64×32, item/handheld 16×16, large 32×32); server still enforces.
5. Slug + display name UX ([../../07-naming-conventions.md](../../07-naming-conventions.md)).
6. Status page via `GET /skins/submissions/{id}`.

## Env

- `NEXT_PUBLIC_API_URL` → ProvinceSystem API  
- Never expose `STAFF_KEY` / `PLUGIN_KEY` to the browser  

Parent design: [../../05-skins-system.md](../../05-skins-system.md).
