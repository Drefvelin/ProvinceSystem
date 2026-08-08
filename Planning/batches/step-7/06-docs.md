# Batch 7.06 — Docs + dry-run note

**Plan + build:** Parent planning / STAGING dry-run for pack writer; tick Step 7 verify boxes when harness is green.

**Repos:** Planning docs (+ STAGING)

**Depends on:** [05-harness-verify](./05-harness-verify.md)

## Plan

1. Confirm parents already link Step 7 / Step 8 split (from docs pass); fix any drift.
2. Add short **dry-run** bullets to [`STAGING.md`](../../../STAGING.md) or [06-local-development](../../06-local-development.md): run harness → inspect Copy/temp; no Discord required.
3. Mark Step 7 index / [08](../../08-implementation-checklist.md) S4a boxes when harness verified (operator).

## Build

| File | Action |
|------|--------|
| `STAGING.md` or `06-local-development.md` | harness dry-run |
| `08` / step-7 `00-index` | verify checkboxes |

## Verify

- Docs describe Step 7 end state vs Step 8  
- Harness run instructions copy-paste clean (no `#` inside bash fences)  

## Out of scope

Implementing Step 8 plugin integrate.
