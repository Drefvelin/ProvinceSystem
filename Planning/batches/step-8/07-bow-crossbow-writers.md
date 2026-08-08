# Batch 8.07 — Bow / large_bow / crossbow writers

**Plan + build:** Pack writers + harness for `bow`, `large_bow`, `crossbow`; wire into ArmourShop apply path.

**Repos:** `Workspace/armourshop` (+ API sizes if needed)

**Depends on:** [06-docs-e2e](./06-docs-e2e.md) (melee/armor path green) · research IA bow/crossbow in TFMC packs

## Plan

1. Research live/Copy IA patterns: BOW material + pull textures (`iasurvival` colored bows; TFMC `tfmc_pack` bow/crossbow models). Lock PNG counts/sizes and whether `generate: true` or thin models + overrides.
2. Add `PackKind` values `BOW`, `LARGE_BOW`, `CROSSBOW` (or equivalent) and writers under `pack/`.
3. Fixture / extend `PackHarnessMain` for all three kinds (`base_set` shortbows / longbows / crossbows).
4. Wire apply pipeline (03) to call new writers instead of skip; shop YAML already uses `ps_items` + `item:` path.
5. Confirm API pixel rules for each kind (likely 16×16 bow, 32×32 large_bow — lock after research); update frontend sizes if needed.
6. Staging smoke: upload → approve → pull → reload → apply onto shortbow / longbow / crossbow BaseSet gear.

## Build

| File | Action |
|------|--------|
| `pack/*Writer*.java` + kinds | create |
| Grip/templates or pull textures | as required by IA research |
| `PackHarnessMain` | assert new kinds |
| Apply service | remove skip for bow kinds |
| API / frontend sizes | align if locked sizes differ |

## Verify

```bash
cd Workspace/armourshop
mvn -DskipTests package
java -cp target/classes net.tfminecraft.ArmourShop.pack.PackHarnessMain
```

- [x] Harness: bow / large_bow / crossbow fixtures under `tfmc_submissions`  
- [x] Multi-frame naming (`{id}.png` + `_0/_1/_2` [+ `_charged`]); mismatched id rejected  
- [x] Apply + shop wired (no skip)  
- [ ] Staging: shortbows / longbows / crossbows skin applies in shop  

**Locked:** bow/crossbow 16×16 (4 / 5 PNGs); large_bow 32×32 (4 PNGs). Writers: `BowWriter` / `CrossbowWriter` (`generate: true`); `LargeBowWriter` (`generate: false` + enlarged display).

## Out of scope

Guns (rifles/pistols/shotguns/launchers); shields; helmets; re-enabling `item` kind.
