# Batch 2.08 — Verify and handoff to Step 3

**Plan + build:** One documented E2E curl path (or small script); mark Step 2 done; note Step 3 branch/UI work.

Depends on [06-asset-rules](./06-asset-rules.md) and [07-review-sheet](./07-review-sheet.md).

## Plan

1. Add `backend/scripts/skins_e2e_smoke.ps1` (Windows-first) or `.sh` that:
   - seeds if needed
   - redeems
   - uploads **correct-size** fixtures for `armor_set` (16×16 icons, 64×32 layers)
   - uploads one `large_handheld` 32×32 + `grip_preset`
   - fetches review-sheet PNG for each
   - approves armor
   - checks plugin approved
   - marks applied / confirms list update
2. Update [../../08-implementation-checklist.md](../../08-implementation-checklist.md) S1 checkboxes to done when smoke passes (in the same PR as smoke, or manually).
3. Handoff note for Step 3:
   - Branch: stay on `skins-api` for UI **or** open `skins-ui` from updated `skins-api`/`site-rework`
   - First UI batch: redeem + kind picker (`armor_set` / `item` / `handheld` / `large_handheld` + grip) talking to these endpoints
   - Env: `NEXT_PUBLIC_API_URL`, never expose staff/plugin keys

## Build

| File | Action |
|------|--------|
| `backend/scripts/skins_e2e_smoke.ps1` (Windows-first) or `.sh` | create |
| Optional `batches/step-3/00-index.md` stub | create pointing at UI batches TBD |

## Verify

- [ ] Smoke script exits 0 on clean local API  
- [ ] Step 2 checkpoint from [00-index](./00-index.md) satisfied  
- [ ] Ready to start Step 3 without blocking on Discord/ArmourShop  

## Step 2 exit criteria

```text
[x] SQLite + data volume
[x] Naming + secrets
[x] Issue / redeem / seed
[x] armor_set + item/handheld/large_handheld upload with fixed stems
[x] Exact pixel sizes + grip_preset
[x] Staff review-sheet PNG
[x] Staff approve/deny
[x] Plugin approved + applied stubs
[x] Smoke path documented/automated
```
