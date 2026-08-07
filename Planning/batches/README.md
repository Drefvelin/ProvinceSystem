# Implementation batches

Each batch is **one plan + one build**: small enough to finish and verify before the next.

**Branch (Step 2):** `skins-api` (off `site-rework`). ProvinceSystem only.

| Batch | Step | Title | Done when |
|-------|------|-------|-----------|
| [step-2/00-index](./step-2/00-index.md) | 2 | Step overview | — |
| [step-2/01-data-foundation](./step-2/01-data-foundation.md) | 2 | SQLite, paths, compose | DB opens; `data/skins/` exists |
| [step-2/02-naming-and-secrets](./step-2/02-naming-and-secrets.md) | 2 | Slug rules + env keys | Unit-check slug; keys load from env |
| [step-2/03-codes](./step-2/03-codes.md) | 2 | Issue, redeem, seed | Mock code redeems to a session |
| [step-2/04-submissions](./step-2/04-submissions.md) | 2 | Upload armor_set / item_2d (historical) | Files on disk with fixed stems |
| [step-2/05-review-and-pull](./step-2/05-review-and-pull.md) | 2 | Status, staff approve/deny, plugin pull | Approve via curl; approved list works |
| [step-2/06-asset-rules](./step-2/06-asset-rules.md) | 2 | Exact sizes; item/handheld/large_handheld + grip | Wrong size 400; grip stored |
| [step-2/07-review-sheet](./step-2/07-review-sheet.md) | 2 | Staff 2D contact PNG | `review-sheet` returns image/png |
| [step-2/08-verify-handoff](./step-2/08-verify-handoff.md) | 2 | E2E smoke + handoff | Step 2 checkpoint green → Step 3 UI |
| [step-3/00-index](./step-3/00-index.md) | 3 | Skins UI overview | — |

**Later:** Step 3 UI batches; bot / ArmourShop batches as needed.

Parent playbook: [../README.md](../README.md) · Checklist: [../08-implementation-checklist.md](../08-implementation-checklist.md)
