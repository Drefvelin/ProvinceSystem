# Step 56.05 — Declare flow (no code)

**Step:** 56 · **Repo:** SF

## Goal

Wire diplomacy **Declare War** to War v2 + validator. **No declare code** in this step.

## Scope

- [x] `config.yml`: `war.require_declare_code: false` (default)
- [x] `RelationView` declare slot: call `WarGoalValidator` then create `War` v2
- [x] Keep opinion threshold (≤ -50); fix `numOnline() < 0` bug → use `< 1` if online check desired
- [x] Civil war path: `endVassalage` + `civilWar` flags on main participants
- [x] War goal picker UI: **single goal** for war (replace per-target goal grid for declare; legacy war goal view hidden or stubbed until step 62)
- [x] On success: notify both sides, open war list, `saveWar`

## Out of scope

- Code entry modal → step 68
- Campaign generation → step 57 (war may start with `objectiveProvinceId = null` until 57 hooks in)

## Verify

- [ ] Manual: declare subjugate war between two factions with settlements
- [ ] Manual: annex declare rejected when settlement in de jure target
- [ ] Manual: duplicate war blocked (`exists()`)

## Status

**Done** (2026-08-19). **Next batch:** [56.06 — Participants](./06-participants.md).
