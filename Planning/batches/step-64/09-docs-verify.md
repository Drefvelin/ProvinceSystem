# Step 64.09 — Docs & verify

**Repos:** `Workspace/simplefactions`, `ProvinceSystem/Planning`  
**Depends on:** all 64.02–64.08 batches  
**Touches:** `Wars.md`, `war-build-order.md`, `step-65/00-index.md` (cross-ref only)

## Goal

Documentation matches shipped behavior. Full regression pass.

## Scope

### `Wars.md` updates

- Campaign battle schedule at declare (field cadence, fort ZOC sieges, trim, initiative formula).
- War-time fort control (controller flips on siege; re-siege on counter-push).
- Battle kinds on campaign GUI (Field Battle, Siege).
- Remove: province-leave penalty, allowed province set, spawn-in-battle-province requirement.
- Remove or strike: coastal fort alignment (point to step 65 for naval).
- Update build steps table: step 64 scope as in [00-index](./00-index.md).

### Planning

- Mark batches 64.01–64.09 status in [00-index](./00-index.md).
- Ensure [step 65](../step-65/00-index.md) references 64 schedule + fort control as dependency.

### Tests

- `mvn test` green.
- Manual staging checklist:
  1. Declare war crossing fort → schedule shows siege + objective.
  2. Trim visible when route long (many field slots).
  3. Fight siege → fort controller flips in debug output.
  4. Campaign GUI lore shows Siege / Field Battle.
  5. Battle edit: spawn outside province, start battle, no leave penalty.

## Done when

Docs committed, tests pass, step 64 marked **done** in index.
