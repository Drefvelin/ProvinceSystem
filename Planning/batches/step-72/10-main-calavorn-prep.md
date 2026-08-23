# Step 72.10 — Calavorn (`main`) data prep

**Plan + operator runbook + optional one-time data commit**  
**Depends on:** [09-save-upload-regen](./09-save-upload-regen.md)  
**Playbook:** [17-map-title-editor.md](../../17-map-title-editor.md)

## Goal

Prepare `main` (Calavorn) for lore staff: clear incorrect duchy/kingdom/empire data; keep counties; document rename + rebuild procedure.

## Context

| File | Current state (`main`) |
|------|------------------------|
| `county.json` | ~64 counties - **geometry OK, names need lore pass** |
| `duchy.json` | ~24 duchies - **wipe and rebuild** |
| `kingdom.json` | exists - **wipe** |
| `empire.json` | exists - **wipe** |

## Deliverables

### 1. Backup snapshot

Before wipe, copy to Planning archive or `defines/main/_backup_pre_editor/`:

- `duchy.json`, `kingdom.json`, `empire.json`

Not required in git long-term; operator may keep local backup.

### 2. Data wipe commit (optional batch step)

Replace:

```json
{}
```

or remove all keys from `duchy.json`, `kingdom.json`, `empire.json` in [`defines/main/`](../../../backend/src/defines/main/).

**Do not** modify `county.json` in this batch unless coordinated with lore team.

### 3. Regen after wipe

Run (staging then production):

```text
fullregen:duchy
fullregen:kingdom
fullregen:empire
```

Or single `fullregen` if operator prefers full rebuild.

Verify `/map/main` duchy/kingdom/empire modes show empty or fallback.

### 4. Operator runbook (in doc)

Add section to [17-map-title-editor.md](../../17-map-title-editor.md) or STAGING:

**Phase A - County rename (lore staff)**

1. Open `/map/editor`, map `main`, tab County.
2. For each county: select → set lore name → adjust colour if needed → Save.
3. Regenerate `fullregen:county`.
4. Check `/map/main` county mode labels.

**Phase B - Rebuild duchies**

1. Tab Duchy → New → name + colour → click counties → Save.
2. Repeat for all duchies.
3. Regenerate `fullregen:duchy`.

**Phase C - Kingdom and empire**

Same pattern for kingdom and empire tabs.

**Phase D - QA**

- Every province in exactly one county (spot check + optional script).
- No duplicate rgb within tier.
- Labels readable on `/map/main` for all political modes.

### 5. Optional validation script

[`backend/src/scripts/util/validate_title_coverage.py`](../../../backend/src/scripts/util/validate_title_coverage.py):

- All provinces from `provinces.txt` assigned to exactly one county.
- All counties referenced by at most one duchy (when duchy file non-empty).
- Print report for operator.

CLI: `python -m src.scripts.util.validate_title_coverage main`

## Done when

- `main` duchy/kingdom/empire empty in repo (if wipe committed).
- Runbook in STAGING Step 72.
- Validation script runs green on counties-only state.

## Status

Done.
