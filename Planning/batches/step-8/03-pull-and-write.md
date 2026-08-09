# Batch 8.03 — Pull approved + pack write

**Plan + build:** ArmourShop fetches approved submissions, downloads PNGs, calls Step 7 writers onto `ia-contents-path` for kinds that already have writers.

**Repos:** `Workspace/armourshop`

**Depends on:** [02-base-set-ui](./02-base-set-ui.md) · Step 7 writers

## Plan

1. Extend `ProvinceSystemClient`: `GET /skins/plugin/approved`, file download, parse `kind`, `slug`, `display_name`, `grip_preset`, `base_set`, `files`, `player_uuid`.
2. Map stems → `PackSubmission` (+ `GripPreset` for large):
   - `armor_set` → `ArmorSetWriter`
   - `handheld` → `FlatItemWriter` (HANDHELD)
   - `large_handheld` → `LargeHandheldWriter`
3. **`bow` / `large_bow` / `crossbow`:** skip or fail-closed with clear log until [07](./07-bow-crossbow-writers.md); do not ack those ids.
4. Target `Cache.iaContentsPath` (live or Copy dry-run). Carry `base_set` through for shop (04) even though pack writers do not need it for textures.
5. Entry: admin command and/or periodic task; log per id.
6. Do **not** ack applied yet (05); do **not** write shop/LP yet (04).

## Build

| File | Action |
|------|--------|
| `ProvinceSystemClient.java` | approved + download |
| Pack apply service / command | orchestrate writers; skip bow kinds |
| `config.yml` | ensure `pack-apply.ia-contents-path` set for env |

## Verify

```bash
cd Workspace/armourshop
mvn -DskipTests package
```

In game (admin): `/armourshop pack pull` with `skins-api.*` + `pack-apply.ia-contents-path` set.

- [x] Client: list approved + download files  
- [x] Writers for armor / handheld / large; bow kinds skipped  
- [x] `/armourshop pack pull` + tab  

**Implemented:** `ProvinceSystemClient.listApproved` / `downloadSubmissionFile`; `PackApplyService`; admin `pack pull`.

## Out of scope

Shop YAML; LP; IA reload; `POST /plugin/applied`; bow writers (07).
