# Batch 19.01 — Attribute point-buy sheet (RPCharacters)

**Plan + build:** Replace `attributes_selection_stage` (discrete `str1`/`str2`… picks) with an in-game **attribute sheet**: spend exactly 12 points across six stats with escalating cost. Web will mirror this after catalog sync.

**Repos:** `Workspace/rpcharacters`

**Depends on:** Current `stages.yml` / `traits/attributes-traits.yml` / `config.yml` attributes list

## Locked formula

| Rule | Value |
|------|-------|
| Stats | strength, dexterity, constitution, intelligence, wisdom, charisma |
| Pool | **12** — must spend **exactly** 12 |
| Max rank / stat at creation | **+2** |
| Cost of *n*-th rank in one stat | **n** (1 then 2) |
| +2 in one stat | costs **3** |
| Six×+2 | **18** > 12 → specialization |

## Plan

1. **New stage type** — e.g. `attributes` / `point_buy` (not `selection`).
2. **In-game GUI** — one inventory/sheet: six attributes, current rank, cost of next +, remaining points, confirm when pool == 0 remaining (exactly spent).
3. **Persist** — apply `attribute-modifiers` equivalent to today’s per-rank `.1` bumps; character stores ranks (or derived trait ids). Prefer ranks map for clarity + web parity.
4. **stages.yml** — change `attributes_selection_stage` to the new type; drop reliance on selecting `str1`/`str2` items for creation.
5. **Summary / edit** — summary entry still editable; reopen sheet with spent points hydrated.
6. **Keep** personality/physical/etc. as selection stages.

## Verify

- [x] In-game create: cannot finish attributes until exactly 12 spent *(enforced in `AttributesStage.confirm`)*  
- [x] Cannot raise any stat above +2  
- [x] +1 costs 1, +2 costs +2 more; refunds restore points correctly  
- [x] Finish applies modifiers via existing `str1`/`str2`… traits  
- [x] Existing characters with old attribute traits hydrate on summary edit  
- [ ] Operator: deploy jar and smoke create/edit on staging  

## Implemented

- `StageType.ATTRIBUTES` + `AttributesStage` point-buy sheet (pool 12, max-rank 2)
- GUI +/- sheet in `InventoryManager`; clicks in `CreationManager`
- `stages.yml` `attributes_selection_stage` → `type: attributes`

## Out of scope

Web UI; catalog sync; personality redesign.
