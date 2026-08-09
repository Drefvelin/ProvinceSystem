# Batch 13.07 — Docs verify + smoke

## Staging checklist

- [ ] Upload `item_3d` (texture + model) → approve → apply → skin in ArmourShop (`ps_items`)
- [ ] Upload `shield` → apply → idle + blocking models in `tfmc_submissions`
- [ ] Upload `helmet_3d` → apply → `set: helmets`
- [ ] Upload `armor_set` with one flat + one 3D-helmet tier → both SkinSets apply
- [ ] Staff delete removes model JSON + blocking + 3D helmet assets

## Harness

```text
mvn -DskipTests compile exec:java -Dexec.mainClass=net.tfminecraft.ArmourShop.pack.PackHarnessMain
```

## Status

Step 13 implementation complete. Guns and multi-view bake remain later.
