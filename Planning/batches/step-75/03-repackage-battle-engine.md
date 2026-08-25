# Step 75.03 — Repackage `War/battle/engine`

**Depends on:** [75.02](./02-repackage-schedule.md) (can run in parallel if no merge conflicts; sequential is safer)  
**Status:** **done** (2026-08-24)

## Scope

Split flat `War/battle/engine` into `core`, `capture`, `win`, `raid` per [01-planning-lock.md](./01-planning-lock.md). **No logic edits.**

## Steps

1. Create subpackages under `War/battle/engine/`.

2. Move files per migration map.

3. Update imports in:
   - Remaining `engine/*` cross-references
   - `War/battle/campaign/*`
   - `War/battle/military/*`
   - `War/battle/persistence/*`
   - `War/battle/ui/*`
   - `War/campaign/progression/*` or `War/progression/*` (battle end hooks)
   - All battle tests under `src/test/.../War/battle/**`

4. Keep `Battle.java` and `BattleManager.java` in `engine/core` (not `engine` root).

5. Grep for stale imports:
   ```text
   import me.Plugins.SimpleFactions.War.battle.engine.FieldWinService
   ```
   (should become `.engine.win.FieldWinService`, etc.)

## Verify

```bash
cd simplefactions && mvn test -Dtest="me.Plugins.SimpleFactions.War.battle.**"
cd simplefactions && mvn test -Dtest="me.Plugins.SimpleFactions.War.**"
```

## Done when

- [x] No `.java` files remain directly under `War/battle/engine/` (only subfolders)
- [x] Each subpackage ≤12 files
- [x] Battle + War tests green
