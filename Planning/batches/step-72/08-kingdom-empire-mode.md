# Step 72.08 — Kingdom and empire modes

**Build:** ProvinceSystem frontend  
**Depends on:** [07-duchy-mode](./07-duchy-mode.md)  
**Playbook:** [17-map-title-editor.md](../../17-map-title-editor.md)

## Goal

**Kingdom** and **Empire** tiers with same UX as duchy mode, picking child titles and painting rolled-up provinces.

## Deliverables

### Kingdom mode

| Piece | Detail |
|-------|--------|
| Pick map | `mapdata/duchy` |
| Members | `titles[]` → duchy ids |
| Paint | Resolve duchy → counties → provinces via `resolveDuchyProvinces` |
| Assignment | `duchyToKingdomId` |

### Empire mode

| Piece | Detail |
|-------|--------|
| Pick map | `mapdata/kingdom` |
| Members | `titles[]` → kingdom ids |
| Paint | Resolve kingdom → … → provinces via `resolveKingdomProvinces` |
| Assignment | `kingdomToEmpireId` |

### Shared `useTitleTierEditor` hook

Consolidate county/duchy/kingdom/empire sidebar + click logic into configurable hook:

```ts
type TierConfig = {
  tier: EditorTier;
  childTier?: EditorTier;
  memberField: "provinces" | "titles";
  pickMode: string;
  resolveMembersToProvinces: (ids, layers) => number[];
};
```

Reduces duplication from 72.06–72.07.

### Tier dependency banners

| Tab | Prerequisite message |
|-----|---------------------|
| Duchy | Counties saved |
| Kingdom | Duchies saved |
| Empire | Kingdoms saved |

## Tests

- `resolveTitleProvinces` integration for paint on kingdom/empire tabs.
- Hook: toggle member updates `titles[]`.

## Done when

- All four tier tabs functional in draft (no upload yet).
- Empire entry with multiple kingdoms paints correctly.

## Status

Done.
