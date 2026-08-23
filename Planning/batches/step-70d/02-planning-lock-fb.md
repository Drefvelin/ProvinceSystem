# Step 70d.02 — Planning lock (FB legs + axis insertion)

**Authority for implementation batches 70d.03–70d.08.**  
Supersedes append-order sections of [01-planning-lock.md](./01-planning-lock.md).

**Status:** **locked** (2026-08-23)

---

## Pipeline overview

```text
pathfinder axis (AC ... B ... DT)
        |
        v
  split two leg segments on axis
        |
        +-- invasion:  FB province -----> DT (defender target / objective)
        |
        +-- counter:   axis[B-1] province -> AC (attacker capital)
        |
        v
  each leg: walk segment, call placeBattle only
        |
        v
  trim each leg to max_battles_per_leg (4)
```

**B** = diplomatic border on axis (`campaignStartProvinceId`, `cursorIndex`).  
**FB** = **first battle** on the invasion leg (the landing fight). Usually the FIELD at B; if a naval battle happens before that fight, NAVAL is list index 0 and the FB field at B stays in the list at index 1.  
**DT** = defender terminal (regional objective or capital per goal rules; same as old "DC" in docs).

Counter leg does **not** include B or FB; it starts one step **toward AC** from B (`cursorIndex - 1`).

---

## Two lists

| Leg | JSON field | Axis segment | Direction | Terminal |
|-----|------------|--------------|-----------|----------|
| **Invasion** | `campaignBattleSchedule` | FB province → DT | increasing index | required FIELD at DT |
| **Counter** | `campaignCounterSchedule` | `axis[cursorIndex-1]` → AC | decreasing index | required FIELD at AC |

**List order = fight chronology = geographic order along that segment** (not discovery order during the walk).

A province may appear **multiple times** on a leg (e.g. siege + required field at same id, or FIELD + SIEGE at fort province).

GUI row order (70c) is unchanged: merge both legs, sort by `campaignProvinces.indexOf(provinceId)`.

---

## Build context contract

`CampaignScheduleBuildContext` holds mutable per-build state. Required fields:

| Field | Purpose |
|-------|---------|
| `List<Integer> axis` | Sort keys for axis-order insertion (**add in 70d.04**; not yet in code) |
| `List<ScheduledCampaignBattle> invasion` | Invasion leg schedule under construction |
| `List<ScheduledCampaignBattle> counter` | Counter leg schedule under construction |
| `int borderProvinceId` | Province id at B (`campaignStartProvinceId`) |
| `int cursorIndex` | Index of B on axis |
| `Set<String> scheduledFortIds` | Fort installation ids already on either leg (cross-leg dedupe) |
| `Set<String> invasionPortIds` / `counterPortIds` | Port ids used for NAVAL on each leg |
| `FortZocIndex fortIndex` | Fort ZOC lookup during walks |

Only `CampaignBattlePlacer.placeBattle` appends or inserts into the invasion/counter lists.

---

## `placeBattle` — only mutation API

```java
void placeBattle(
    CampaignScheduleBuildContext ctx,
    War war,
    ScheduleLeg leg,
    int provinceId,          // battle tile (fort home for SIEGE)
    BattleTrigger trigger,
    CampaignCoalition advancing,
    @Nullable String fortInstallationId,
    @Nullable String portInstallationId)
```

### Insertion rule

After resolving whether a slot is created (dedupe, skip sea land, etc.):

1. Compute **sort key** = `axis.indexOf(provinceId)` (for NAVAL use sea province id).
2. **Insert** the new slot at the smallest index `i` such that all existing slots at `i..` have axis index **greater than** sort key, **or** equal axis index but **lower kind priority** (see tie-breaking below).
3. **Naval before FB (invasion only):** if `trigger == NAVAL` and `leg == INVASION`, insert at index **0** regardless of sort key. FB field at B is not removed.

Fort siege uses **fort home province** as `provinceId` (e.g. Greenfort → **713**, not ZOC tile 709).

### Siege chronology (70d.09)

When fort home is **off-axis**, sort key and GUI geographic position use the **trigger tile** (walk `provinceId` passed to `FORT_ZOC`). On-axis homes continue to sort by fort home province.

| Field | Rule |
|-------|------|
| `provinceId` | Fort home (battle location) |
| `chronologyProvinceId` | Trigger tile when fort home is **off-axis**; null when home is on-axis or same as trigger |
| Sort key | `axis.indexOf(chronologyProvinceId ?? provinceId)` |

**Invasion guard:** skip `FORT_ZOC` when `axis.indexOf(trigger) > objectiveAxisIndex` (never schedule past DT).

### Same-axis-index tie-breaking

When two slots share the same `axis.indexOf(provinceId)`, order within that province (lower number = earlier in list = fought first):

| Priority | Kind | Notes |
|----------|------|-------|
| 1 | `SIEGE` | Fort battle before field battles at same province |
| 2 | `FIELD` optional | CADENCE or BORDER (`required=false`) |
| 3 | `FIELD` required | OBJECTIVE (`required=true`) |
| 4 | `NAVAL` | Invasion prepend rule overrides; counter uses axis insert |

Example: siege + required objective at capital DT → `[SIEGE@DT, FIELD required@DT]` when both share the province id.

When sort keys differ, axis index always wins (e.g. siege at **713** inserts before cadence field at **706** because `indexOf(713) < indexOf(706)` on the invasion segment).

### NAVAL per leg

| Leg | Rule |
|-----|------|
| **Invasion** | Always prepend at index **0** (fight before FB landing). FB FIELD at B stays at index 1. |
| **Counter** | Insert at axis index of the sea province (standard insertion rule). No prepend. |

### Dedupe

- `scheduledFortIds` — across both legs
- per-leg port ids for NAVAL
- same leg + same province + FIELD: skip duplicate optional FIELD; OBJECTIVE upgrades existing FIELD to `required`

### Kind mapping

| Trigger | Kind | required |
|---------|------|----------|
| BORDER, CADENCE | FIELD | false |
| OBJECTIVE | FIELD | true |
| FORT_ZOC | SIEGE | false |
| NAVAL | NAVAL | false |

No new `NAVAL_INVASION` slots.

---

## Walk per leg

### Phase 1 — FB anchor (invasion only)

```text
placeBattle(INVASION, borderProvinceId, BORDER)
```

Optional immediately after: if B is in enemy fort ZOC, `placeBattle(INVASION, borderProvinceId, FORT_ZOC)` (siege lands at fort home province via placer).

### Phase 2 — Invasion land walk

Walk axis indices from `cursorIndex` toward `indexOf(DT)`, step +1.

At each step `i`:

1. If `i == cursorIndex`: **skip** cadence and FORT_ZOC (FB and border ZOC handled in phase 1).
2. If `offset % N == 0` from `cursorIndex`: `placeBattle(INVASION, provinceId, CADENCE)`.
3. If province in enemy fort ZOC: `placeBattle(INVASION, provinceId, FORT_ZOC)`.
4. At `indexOf(DT)`: `placeBattle(INVASION, DT, OBJECTIVE)`.

Cadence origin for invasion = `cursorIndex` (FB axis index).

### Phase 3 — Counter land walk

Walk from `cursorIndex` toward `indexOf(AC)`, step -1. **Never** place B.

At each step `i`:

1. If `i == cursorIndex`: skip (counter does not own B).
2. If `offset % N == 0` from `cursorIndex - 1`: `placeBattle(COUNTER, provinceId, CADENCE)`.
3. Fort ZOC: same as invasion but `ScheduleLeg.COUNTER`.
4. At `indexOf(AC)`: `placeBattle(COUNTER, AC, OBJECTIVE)`.

Cadence origin for counter = `cursorIndex - 1`.

### Phase 4 — Sea scans (after both land walks)

Scan sea runs on each leg's axis index range:

- **Invasion** (B → DT): enemy **defender** ports → `placeBattle(INVASION, seaProvinceId, NAVAL)`
- **Counter** (B-1 → AC): enemy **attacker** ports → `placeBattle(COUNTER, seaProvinceId, NAVAL)`

---

## Trim

| Leg | Policy |
|-----|--------|
| Invasion | Drop optional FIELD from DT side first; never drop required; never drop FB FIELD at `campaignStartProvinceId`; if index 0 is NAVAL, also protect index 1 (FB field) |
| Counter | Drop optional FIELD from border-adjacent side first |

---

## Example (Brume vs Lantan)

Axis: `452, 782, 758, 757, 672, 709, 713, 705`. B = 709, DT = 705.

**Invasion chronological list:**

```text
709 FIELD (FB)
713 SIEGE (Greenfort)
705 FIELD required
```

With Lan harbour sea battle: `795 NAVAL` prepended → `[NAVAL@795, 709 FIELD, 713 SIEGE, 705 required]`.

**Counter:** optional fields at 672, 782, …; required 452.

**GUI row (70c):** `452 - 782 - 672 - [709] - 713 siege - 705`

---

## Implementation notes (partial code vs lock)

Partial implementation from 2026-08-23 crash session. **Do not ship** until 70d.04–70d.07 close these gaps:

| Area | Current code | Locked behavior (this doc) |
|------|--------------|----------------------------|
| [`CampaignBattlePlacer`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/schedule/CampaignBattlePlacer.java) | `schedule.add()` / `add(0, naval)` | `insertAtAxisOrder()` using `ctx.axis()` sort key + kind tie-break |
| Counter NAVAL | Appended at end | Inserted at sea province axis index |
| List order | Walk discovery order | Geographic order along leg segment |
| [`CampaignScheduleBuildContext`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/schedule/CampaignScheduleBuildContext.java) | No `axis` field | Must store axis list (70d.04) |
| [`CampaignScheduleBuilder`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/schedule/CampaignScheduleBuilder.java) | Phased walks exist | Walk structure OK; relies on placer fix for ordering |
| Tests | Builder suite failing | Green after 70d.07 |

---

## Done when

- [x] FB vs B documented
- [x] Insert-at-axis rule documented
- [x] Same-axis-index kind tie-breaking documented
- [x] Build context contract documented
- [x] NAVAL per-leg rules documented
- [x] Implementation delta documented
- [x] 70d.03–70d.08 implemented
- [ ] User sign-off after Brume smoke
