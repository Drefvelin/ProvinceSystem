# Step 70b.02 — Cadence config + Brume counter test

**Repos:** `Workspace/simplefactions`  
**Depends on:** [70b.01 planning lock](./01-planning-lock.md)  
**Touches:** `config.yml`, `CampaignScheduleBuilder`, `CampaignScheduleBuilderTest`, optional `WarCampaignServiceTest`

## Goal

Set dev/prod cadence to **3** and prove counter-leg wilderness battles exist on the Brume–Lantan shaped axis.

## Tasks

### 1. Config

```yaml
war:
  battle_cadence:
    first_battle_at_border: true
    provinces_between_battles: 3
```

Update `ConfigLoader` default only if code default should match (optional; config file is source of truth).

Document in [DEV-SHORTCUTS.md](../../DEV-SHORTCUTS.md) dev table: cadence `3` (was `1`).

### 2. Cadence logic audit

Read `CampaignScheduleBuilder.cadenceMatches` + `appendAxisStep`. Confirm behavior matches [70b.01](./01-planning-lock.md):

- Invasion origin = `borderStartIndex`
- Counter origin = `borderStartIndex - 1`
- Terminal province excluded from cadence loop step but gets `required` slot

**Do not** change cadence algorithm unless unit test proves grid mismatch with lock; if change needed, prefer minimal fix and update 70b.01.

### 3. Unit test — Brume counter wilderness

Add `CampaignScheduleBuilderTest.buildCounter_brumeAxis_wildernessCadenceFields`:

```text
axis:     [452, 782, 758, 757, 672, 709, 713, 705]
border:   index 5 (709)
counter:  from 672 → 452
cadence:  3
```

Assert:

- `schedule` non-empty
- At least one `FIELD` slot with `provinceId` in `{672, 757, 758, 782}` and `!required`
- Final slot: `FIELD` at `452`, `required == true`
- No slot at `709` (border is invasion-only)

### 4. Unit test — Brume invasion (short segment)

`build_brumeAxis_invasion_cadenceAndSiege`:

- Border 5 → objective 7
- Expect field at `709`, siege referencing `Greenfort`, required field at `705`
- Slot count ≤ 4 before trim; document natural size

### 5. Integration smoke (optional)

`WarCampaignServiceTest` with mocked Brume/Lantan ownership + Greenfort fort if feasible without huge fixture.

## Done when

- [x] `config.yml` cadence = 3
- [x] Brume counter test green
- [x] Brume invasion test green (siege anchors at border 709 when inside Greenfort ZOC)
- [x] `mvn test` for schedule package passes
