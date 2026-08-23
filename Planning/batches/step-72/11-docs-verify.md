# Step 72.11 — Docs and verify

**Plan + docs + manual QA**  
**Depends on:** [10-main-calavorn-prep](./10-main-calavorn-prep.md)  
**Playbook:** [17-map-title-editor.md](../../17-map-title-editor.md)

## Goal

Close step 72 in hub docs, STAGING, and implementation checklist. Manual QA with lore-staff-style walkthrough.

## Deliverables

### 1. STAGING Step 72

Add to [`STAGING.md`](../../../STAGING.md):

- Staff account with `tfmc.map.staff`.
- Editor URL, save, regen, viewer parity checks.
- Calavorn county rename smoke (one county).
- Non-staff 403 check.

### 2. Hub updates

| Doc | Update |
|-----|--------|
| [Planning/README.md](../../README.md) | Map title editor in reading order |
| [08-implementation-checklist.md](../../08-implementation-checklist.md) | M8 step 72 checklist |
| [16-map-platform.md](../../16-map-platform.md) | Cross-link step 72 |
| [01-current-state.md](../../01-current-state.md) | Editor shipped note (when done) |
| [batches/README.md](../README.md) | Step 72 row |

### 3. DEV-SHORTCUTS (optional)

Local editor dev: API URL, test staff session, regen command without plugin hash.

### 4. Manual QA checklist

```text
[ ] Non-staff: /map/editor → permission gate
[ ] Staff: editor loads main + dev
[ ] County: create, rename, recolour, add/remove province, delete
[ ] Live paint updates on click without regen
[ ] Save → county.json timestamp/content changes
[ ] Regenerate → viewer county colours match editor
[ ] Duchy: combine 2+ counties, save, regen, viewer duchy mode
[ ] Kingdom + empire: one entry each minimum
[ ] Upload route without auth → 403 for county tier
[ ] Unsaved warning on tier switch
[ ] Mobile: pan/zoom usable (desktop-primary OK)
[ ] No em dash in editor UI strings
```

### 5. Close 00-index status

Update [00-index](./00-index.md) to **72.01–72.11 done** when complete.

## Done when

- STAGING Step 72 ticked.
- Checklist in 08-implementation-checklist all `[x]`.
- Lore staff walkthrough recorded (notes in STAGING or batch close-out).

## Status

Done.
