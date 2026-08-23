# Step 65.07 — Docs & verify

**Repos:** `Workspace/simplefactions`, `ProvinceSystem/Planning`  
**Depends on:** all 65.02–65.06 batches  
**Touches:** `Wars.md`, `Installations.md`, `war-build-order.md`, `step-66/00-index.md` (cross-ref only)

## Goal

Documentation matches shipped naval behavior. Full regression pass. Step 65 marked **done**; step 66 unblocked.

## Scope

### `Wars.md` updates

- Implementation status banner: step 65 **shipped** with date.
- [Campaign battle schedule](#campaign-battle-schedule-locked-step-64): add natural slot rows for `NAVAL` and `NAVAL_INVASION`; port coverage radius config.
- [Naval & installations](#naval--installations): remove "ships step 65" future tense; document blocking port + invasion + siege override.
- Build steps table: row 65 **done**.
- Strike any remaining **coastal fort** special-case rules (superseded by port ZOC + fort ZOC).

### `Installations.md`

- War-aware ZOC export marked shipped.
- Port sea ZOC radius config cross-ref.

### Planning

- Mark batches 65.01–65.07 in [00-index](./00-index.md).
- [step 66](../step-66/00-index.md): note step 65 naval schedule as dependency.

### Tests

```bash
cd simplefactions
mvn test
```

Manual staging checklist:

1. Declare war with sea crossing + enemy port → schedule shows Naval Battle at port.
2. Sea crossing → first defender coast shows Naval Invasion (or Siege if fort ZOC).
3. Trim on long amphibious route keeps naval slots over field cadence.
4. Campaign GUI: Naval Battle / Naval Invasion lore.
5. Fight naval slot → field battle with `navalVariant`; staff naval spawn applies.
6. Export `map_markers.json` after siege flip → fort ZOC uses controller coalition.

## Done when

Docs updated, `mvn test` green, step 65 **done** in index and `war-build-order.md`.
