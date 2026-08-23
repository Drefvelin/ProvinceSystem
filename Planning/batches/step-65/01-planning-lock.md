# Step 65.01 — Naval battles & invasions lock

**Plan + docs only.** Lock port sea ZOC, naval / naval-invasion slot rules, siege override on amphibious landing, launch mapping, trim (already in 64), map export controller filter, and optional installation-pick scope before 65.02+ code.

**Repos:** `Workspace/simplefactions`  
**Depends on:** [step 64](../step-64/00-index.md) (shipped 2026-08-23) · [Wars.md](../../../../simplefactions/Documentation/Wars.md) · [Installations.md](../../../../simplefactions/Documentation/Installations.md)

**Status:** **Done** (2026-08-23). Authoritative gameplay summary in [Wars.md](../../../../simplefactions/Documentation/Wars.md) (Campaign battle schedule + Naval & installations).

---

## Locked — extends step 64 schedule model

Step 64 ships `FIELD` and `SIEGE` on the campaign axis. Step 65 adds **`NAVAL`** and **`NAVAL_INVASION`** display kinds to the same `campaignBattleSchedule` pipeline (builder → trim → resolver → launch → GUI).

| Layer | Step 64 | Step 65 add |
|-------|---------|-------------|
| **`BattleType`** | `FIELD`, `SIEGE` | Unchanged — **no `BattleType.NAVAL`** |
| **`CampaignBattleKind`** | `FIELD`, `SIEGE` | `NAVAL`, `NAVAL_INVASION` (enum already exists) |
| **Template flag** | `navalVariant` on battle (staff sea spawn) | Set `true` when kind is `NAVAL` or `NAVAL_INVASION` |

### Mapping (step 65)

| Slot | `BattleType` | `CampaignBattleKind` | Battle flags | Slot metadata |
|------|--------------|----------------------|--------------|---------------|
| Port gate | `FIELD` | `NAVAL` | `navalVariant = true` | `portInstallationId` |
| Amphibious landing | `FIELD` | `NAVAL_INVASION` | `navalVariant = true` | — |
| Fort ZOC landing override | `SIEGE` | `SIEGE` | — | `fortInstallationId` (replaces invasion slot) |
| Field / objective | `FIELD` | `FIELD` | — | unchanged |

Objective and field cadence rules from 64.01 unchanged.

---

## Locked — sea zones & port coverage

Use **`Terrain.SEA`** only (not `Province.isSea()`, which includes rivers/lakes).

| Concept | Rule |
|---------|------|
| **Sea zone** | Province with `terrain == SEA` |
| **Coastal province** | Land province with at least one `SEA` neighbour |
| **Port coverage** | BFS from **SEA neighbours of the port land province**; expand only across `Terrain.SEA` tiles, max depth **`war.port_sea_zoc_radius`** (default **2**) |
| **Blocking port** | Operational port whose owner coalition is **enemy of aggressor** at declare (`CampaignCoalition.AGGRESSOR` perspective, same as fort siege in 64.03) and whose coverage intersects the **sea segment** the campaign axis crosses |

**Oldest port wins** when multiple ports cover the same sea province (same tie-break as fort ZOC: `completedAt` asc, then `id`).

**Friendly port** on the sea segment does **not** insert a naval slot (passage uncontested).

**No port** on a sea segment: no `NAVAL` slot (axis may still include `SEA` provinces from pathfinder pass 2; only insert naval battle when an enemy port blocks).

---

## Locked — natural slot insertion (builder)

Extend `CampaignScheduleBuilder` axis walk (64.03). Per axis index, after fort siege checks:

### 1. Sea segment detection

Scan axis for maximal contiguous runs where `terrain(province) == SEA`. For each run, consider the **entry** coastal province (land before sea) and **exit** coastal province (land after sea).

If no sea run on axis, skip naval logic for that war.

### 2. `NAVAL` (port gate)

When an enemy port blocks the sea run (coverage intersects any sea province in the run):

- Insert **`NAVAL`** at the **port province** (`portInstallationId` on slot).
- Once per port on the line (dedupe by `portInstallationId`, same pattern as fort siege).

Battle is fought at the port's land province; staff use `navalVariant` layout.

### 3. `NAVAL_INVASION` (amphibious landing)

On the **first defender-owned land** province immediately after a sea run (the exit coastal province if defender-owned, else first defender land along axis after the run):

- Insert **`NAVAL_INVASION`** at that province (`required = false`).
- Only one invasion slot per sea crossing (dedupe by exit segment).

Attacker-owned exit coast (rare on axis) does not get invasion slot.

### 4. Interaction with fort ZOC (see 65.04)

If the invasion target province is inside an **enemy-controlled** fort ZOC at declare, **do not** emit `NAVAL_INVASION`; emit **`SIEGE`** at fort province instead (or keep existing siege slot).

### 5. Dedupe & ordering

Insertion order along axis walk: **fort siege** → **naval** → **naval invasion** → **field cadence** (same step as 64). `ensureObjectiveSlot` unchanged.

---

## Locked — trim priority

Already implemented in `CampaignScheduleTrimmer` (64.05). Priority (keep first):

1. Objective (`required`)
2. Siege
3. `NAVAL`
4. `NAVAL_INVASION`
5. Field cadence

Within tier: drop farthest from objective first.

---

## Locked — resolver & launch (65.04 wiring)

```text
resolve(war, slot):
  SIEGE kind -> BattleType.SIEGE
  else -> BattleType.FIELD

launch(war, slot):
  battle.type = resolve(...)
  battle.navalVariant = (kind == NAVAL || kind == NAVAL_INVASION)
```

Copy `portInstallationId` / `fortInstallationId` to battle metadata if staff GUI needs them (optional display field on `Battle`).

**No** `allowedProvinceIds` (removed 64.08).

---

## Locked — war-time fort control on invasion

Reuse `fortControllers` from 64. Same re-siege dynamic insert when counter-push re-enters enemy fort ZOC (64.06). Naval invasion does not bypass fort ZOC.

---

## Locked — `ZocRealm` map export (65.06)

`Markers.export` fort `zoc_provinces` currently uses installation owner faction.

| Case | Export controller |
|------|-------------------|
| Fort not in any active war | Installation owner (unchanged) |
| Fort in active war with `fortControllers` entry | Faction representing **controller coalition** on that war |
| Multiple active wars (edge) | Use war where fort province is on a campaign axis, else owner |

Implement `ZocRealm.computeZocProvincesForExport(fort, warContext)` or pass resolved controller faction into existing `computeZocProvinces`.

**Ports / airports:** no ZOC export change.

---

## Locked — slot persistence

Extend `ScheduledCampaignBattle` (JSON on `War`):

| Field | Type | When |
|-------|------|------|
| `portInstallationId` | string? | `NAVAL` slots |
| `fortInstallationId` | string? | `SIEGE` slots (unchanged) |

Backward compatible: missing fields → null on load.

---

## Locked — config

```yaml
war:
  port_sea_zoc_radius: 2   # sea-hop BFS from port province
```

Existing `port-sea-proximity-blocks` (construct validation) unchanged.

---

## Optional / deferred (not blocking 65.07)

| Feature | Decision |
|---------|----------|
| Per-battle port / airport / fort **pick** UI | **Defer** unless time remains after 65.06. Slot carries `portInstallationId` for the **blocking** port only; full attacker/defender pick ships later or in 66 prep. |
| Coastal fort doc cleanup | Strike remaining coastal-fort special-case prose in `Wars.md` / `Installations.md` in 65.07 |
| `battle_scheduled` map export payload | Step **67** |

---

## Locked — test scenarios

1. Axis with sea run + enemy port covering sea → schedule contains `NAVAL` at port province.
2. Axis sea run, friendly port only → no `NAVAL` slot.
3. Sea run → first defender land → `NAVAL_INVASION` slot.
4. Invasion province in enemy fort ZOC → `SIEGE` at fort, no `NAVAL_INVASION`.
5. Trim: 6 natural slots, max 4 → keeps objective, siege, `NAVAL`; drops field cadence before `NAVAL_INVASION` if needed (per trimmer).
6. Launch `NAVAL` → `BattleType.FIELD`, `navalVariant = true`.
7. Map export: fort controller flipped in war → `forts[].zoc_provinces` uses controller coalition realm, not owner.

---

## Out of scope (explicit)

- Inter-battle raids (step 66)
- Raid war type (step 66)
- Chronicle / `wars[]` occupation export (step 67)
- Declare codes (step 68)
- New pathfinder passes or multi-route choice at declare
