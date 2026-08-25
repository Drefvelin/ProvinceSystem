# Step 75.06 — Docs and verify

**Depends on:** [75.04](./04-repackage-campaign-tree.md) (and [75.05](./05-merge-micro-types.md) if run)  
**Status:** done (2026-08-24)

## Tasks

1. Merge [`simplefactions/AGENTS.md`](../../../../simplefactions/AGENTS.md) (agent + contributor layout guide).
2. Add Cursor rule [`.cursor/rules/simplefactions-structure.mdc`](../../../../.cursor/rules/simplefactions-structure.mdc) pointing at AGENTS.md for `SimpleFactions/**/*.java`.
3. Update [war-build-order.md](../../war-build-order.md): add step **75** row, status when done.
4. Update this step index [00-index.md](./00-index.md) batch statuses.
5. Grep monorepo for stale packages:
   ```text
   War.schedule
   War.progression
   War.battle.engine.FieldWin
   ```
6. Optional: add one line to [`Wars.md`](../../../../simplefactions/Documentation/Wars.md) dev section: "Source layout: see `simplefactions/AGENTS.md`."

## Automated verify

```bash
cd simplefactions && mvn test
```

## Manual smoke (unchanged from 70d)

After deploy on dev server:

1. `/faction warpath <Brume-Lantan war id>`
2. Campaign GUI row: `452 - 782 - 672 - [709] - 713 siege - 705`
3. Invasion list: `709 FIELD` → `713 SIEGE` → `705 required`

Reorganization must not change these outcomes.

## Done when

- [x] AGENTS.md and cursor rule in repo
- [x] war-build-order lists 75 as **done**
- [x] Full SF test suite green
- [x] No remaining `War/schedule` or `War/progression` paths in source (grep `simplefactions/src/**/*.java`: 0 matches; stale paths only in historical planning batches)
