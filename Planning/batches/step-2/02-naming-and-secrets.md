# Batch 2.02 — Naming and secrets

**Plan + build:** Slug validation + env-based plugin/staff keys. Still no full skins router surface (helpers only, or tiny health that reads config).

## Plan

1. Implement `naming.py` from [07-naming-conventions.md](../../07-naming-conventions.md):
   - Regex `^[a-z][a-z0-9_]{1,47}$`
   - Reject `__`, reserved list (`test`, `texture`, `null`, …)
   - `assert_slug(slug)` → raise clear error / return validation result
   - Optional `slugify_display_name` for later UI (ok to include now)
2. Implement `auth.py` (or `settings.py`):
   - `PLUGIN_KEY`, `STAFF_KEY` from environment (fail loud in prod if missing; for local allow defaults only if `SKINS_DEV=1` or document required `.env`)
   - Helpers: `require_plugin_key(header)`, `require_staff_key(header)`
3. Document local env in a one-line note under batch verify (e.g. `.env` next to backend — do not commit secrets).

## Build

| File | Action |
|------|--------|
| `backend/src/skins/naming.py` | create |
| `backend/src/skins/auth.py` | create |
| Optional tiny test or `__main__` checks | slug accept/reject examples from doc 07 |

## Verify

- [ ] `blue_knight` ok; `BlueKnight`, `blue-knight`, `texture`, `1abc` rejected
- [ ] With env keys set, helper accepts matching `X-Plugin-Key` / `X-Staff-Key` and rejects wrong values

## Out of scope

Code issue/redeem endpoints, file uploads.
