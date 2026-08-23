# Step 73.07 — Docs and verify

**Plan + docs + manual QA**  
**Depends on:** [06-canvas-paint-perf](./06-canvas-paint-perf.md)  
**Playbook:** [17-map-title-editor.md](../../17-map-title-editor.md)

## Goal

Update hub docs, STAGING, and checklist for revised editor UX and performance expectations.

## Deliverables

### 1. STAGING Step 72 amendments

[`STAGING.md`](../../../STAGING.md) Step 72 section:

- Entry: **Edit titles** from map page (not global nav).
- URL pattern: `/map/editor?map=main` (required `map`).
- Remove checklist items that assume nav "Map editor" link.
- Add layout check: no horizontal scroll at 1280px.
- Add perf smoke: county click paint responsive after load.

### 2. Playbook and lock amendments

| Doc | Update |
|-----|--------|
| [17-map-title-editor.md](../../17-map-title-editor.md) | Entry flow, locked map, no nav link |
| [step-72/01-planning-lock.md](../step-72/01-planning-lock.md) | Superseded nav/map-selector note |
| [DEV-SHORTCUTS.md](../../DEV-SHORTCUTS.md) | Editor entry via `/map/main` → Edit titles; UI dev pair |
| [08-implementation-checklist.md](../../08-implementation-checklist.md) | Check 73.01–73.07 |
| [batches/README.md](../README.md) | Step 73 row |
| [01-current-state.md](../../01-current-state.md) | Editor entry UX one-liner |

### 3. Manual QA checklist

```text
[ ] SiteHeader: no Adavaar, no Map editor
[ ] /map/main staff: Edit titles visible -> ?map=main
[ ] /map/r3b1rth staff: Edit titles -> ?map=dev
[ ] /map/editor bare URL: redirect or gate (not silent main edit)
[ ] Editor: no map dropdown; read-only Calavorn / Adavaar label
[ ] Layout 1280px: no body horizontal scroll
[ ] County: load then click provinces - responsive paint
[ ] Tier switch + save/regen still work
[ ] UI dev local: edit CTA + editor without redeem
[ ] No em dash in new UI strings
```

### 4. Close 00-index

Mark **73.01–73.07 done** when complete.

## Done when

- Docs consistent with shipped UX.
- STAGING and checklist updated.
- Operator notes include `provinces.png` dimensions + index build time observed on staging.

## Status

**Done.** STAGING Step 72 amended; hub docs, checklist, and README updated. Automated tests pass (`app/lib/map/editor/`, `test_editor_routes`). Manual QA checklist above for staging operator sign-off.
