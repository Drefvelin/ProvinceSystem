# Step 65.03 — Naval invasion slots

**Repos:** `Workspace/simplefactions`  
**Depends on:** [65.02 port ZOC](./02-port-zoc-naval-slots.md)  
**Touches:** `CampaignScheduleBuilder`, tests

## Goal

After a sea segment on the campaign axis, insert **`NAVAL_INVASION`** at the first **defender-owned land** landing province.

## Scope

### Detection

For each maximal `Terrain.SEA` run on the axis:

1. Find **exit** side: first land province after the run (walking toward objective).
2. If that province is **defender-owned** at declare → schedule `NAVAL_INVASION` there.
3. If exit coast is attacker-owned, scan forward along axis for first defender land; schedule there if within the same "amphibious operation" (before next sea run or objective).

### Slot shape

```text
ScheduledCampaignBattle(provinceId, NAVAL_INVASION, required=false, fortInstallationId=null, portInstallationId=null)
```

`battleType()` remains `FIELD` (existing record logic).

### Dedupe

- One `NAVAL_INVASION` per sea crossing (keyed by sea run start index or entry coastal province).
- Do not add if same province already has a `FIELD` cadence slot (merge: keep `NAVAL_INVASION` kind over plain `FIELD` when both would apply).

## Tasks

1. Sea-run exit / defender-land helper.
2. Builder insertion after naval gate slots for the same run.
3. Unit tests: land–sea–defender land axis → invasion slot on defender coast.
4. Unit tests: land–sea–attacker land–defender land → invasion on first defender land.

## Out of scope

- Fort ZOC override (65.04)
- Launch `navalVariant` (65.04)

## Done when

Test wars with amphibious axis show `NAVAL_INVASION` in natural schedule (pre-trim).
