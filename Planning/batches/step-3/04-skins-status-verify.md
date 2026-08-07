# Batch 3.04 — Status + Step 3 verify

**Plan + build:** Owner status view; close Step 3 with a browser checklist.

## Plan

1. Status UI: `GET /skins/submissions/{id}` with Bearer session — show kind, slug, display_name, grip_preset, status, deny_reason, timestamps.
2. After upload, land on status (same page step or `/skins/status/[id]` — pick one and stick to it; prefer **same `/skins` wizard step** or `/skins/[id]` for shareable-ish URL within session).
3. Locked choice: **`/skins/[id]`** status page (owner session required; 401/404 if wrong session).
4. Copy for pending / denied / approved / applied (approved/applied may appear after staff/plugin — still show if API returns them).
5. Step 3 exit checklist (below); optional short note in [../../08-implementation-checklist.md](../../08-implementation-checklist.md) S2 when done.

## Build

| File | Action |
|------|--------|
| `frontend/app/skins/[id]/page.tsx` | status |
| `frontend/components/skins/StatusCard.tsx` | create |
| `frontend/lib/skins/api.ts` | `getSubmission(id)` |
| Upload success redirect | to `/skins/{id}` |

## Verify (browser)

With local API + `NEXT_PUBLIC_API_URL`:

- [ ] `/` hub + nav; Map / Skins work  
- [ ] R3B1RTH not in nav; direct URL OK  
- [ ] Redeem → upload armor → `/skins/{id}` shows `pending`  
- [ ] Large handheld + grip path works once  
- [ ] Denied reason shows if staff denies via curl (optional)  

## Step 3 exit criteria

```text
[x] Shell + hub (not map redirect)
[x] Public map in nav; r3b1rth unlisted
[x] Skins redeem + session
[x] Upload kinds + sizes + grip
[x] Status page for owner
```

## Out of scope

Discord cog, ArmourShop apply, 3D/shield UI, map perf (A1).
