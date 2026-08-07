# Step 2 — Skins API (batch index)

**Repo:** ProvinceSystem  
**Branch:** `skins-api`  
**Goal:** Backend can run Flow 2 through “approved” with curl only (no Discord, no ArmourShop, no Next UI).

Parent design: [../../05-skins-system.md](../../05-skins-system.md), [../../07-naming-conventions.md](../../07-naming-conventions.md).

## Scope

| In | Out |
|----|-----|
| SQLite + disk under `backend/src/data/` | Frontend `/skins` (Step 3) |
| `armor_set` + `item` + `handheld` + `large_handheld` | `item_3d`, `shield` |
| Exact PNG sizes + `grip_preset` | Discord cog / webhook |
| Staff **review-sheet** PNG (2D contact) | 3D multi-view bake / site WebGL viewer |
| Plugin issue + redeem + staff keys | Writing ItemsAdder files |
| Plugin `GET approved` + applied | ArmourShop Java |

Note: batch [04](./04-submissions.md) historically used `item_2d`; [06-asset-rules](./06-asset-rules.md) retires it.

## Batch order

1. [01-data-foundation](./01-data-foundation.md)  
2. [02-naming-and-secrets](./02-naming-and-secrets.md)  
3. [03-codes](./03-codes.md)  
4. [04-submissions](./04-submissions.md)  
5. [05-review-and-pull](./05-review-and-pull.md)  
6. [06-asset-rules](./06-asset-rules.md)  
7. [07-review-sheet](./07-review-sheet.md)  
8. [08-verify-handoff](./08-verify-handoff.md)  

Do not start batch *N+1* until batch *N* verification passes.

## Suggested layout after Step 2

```text
backend/
  server.py                         # include skins_router
  src/
    api/skins_routes.py
    skins/
      db.py                         # sqlite connect + migrate
      schema.sql
      naming.py
      auth.py                       # plugin/staff/session checks
      codes.py
      submissions.py
      storage.py                    # write fixed-stem files + size checks
      review_sheet.py               # 2D contact PNG for staff
    data/                           # gitignored runtime
      province.db
      skins/
```

Exact module split can vary; keep skins logic out of map routers.

## Final checkpoint (all batches)

```text
seed mock code → redeem → POST armor_set (correct-size PNGs) → files named {slug}_*.png
→ GET review-sheet (staff) → staff approve → GET plugin/approved returns that submission
(+ large_handheld + grip_preset path covered in smoke)
```

Then merge/PR into `site-rework` when ready, and start Step 3 on a UI branch (e.g. `skins-ui` or stay on `skins-api` if you prefer one branch for API+UI).
