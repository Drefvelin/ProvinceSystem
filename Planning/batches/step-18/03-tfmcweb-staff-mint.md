# Batch 18.03 — TFMCWeb `/token create skin staff`

**Plan + build:** Staff mint command on TFMCWeb; permission-gated; hits API staff code mint.

**Repos:** `Workspace/tfmcweb`

**Depends on:** [02-staff-token-api](./02-staff-token-api.md)

## Plan

1. Extend `/token create` tab: `skin` | `character` | **`skin staff`** (or `/token create skin` with subarg `staff`).
2. Permission: `tfmcweb.token.create.staff` (in addition to or instead of plain create — staff requires the staff node).
3. Call codes API with staff flag; click-to-copy same as player mint.
4. Help text: staff codes unlock category/scroll on the website; auto-apply to curated pack.
5. Player `/token create skin` unchanged.

## Build

| Area | Action |
|------|--------|
| `TokenCommand` + `plugin.yml` | staff subcommand + perm |
| client | mint with staff flag |

## Verify

- [x] Without perm → denied  
- [x] With perm → code redeems as staff session  
- [x] Player mint still non-staff  

## Implemented

- `/token create skin staff` → `POST /skins/codes` `scope=skin_staff`
- Perm `tfmcweb.token.create.staff` (staff-only; does not require `tfmcweb.token.create`)
- Command YAML gate removed so staff-only LP can invoke `/token`; gates inside `TokenCommand`
- `ProvinceSystemClient.issueFeatureCode` allows `skin_staff`
- Player `/token create skin|character` unchanged (`tfmcweb.token.create`)

## Out of scope

Website dropdowns; pack apply.
