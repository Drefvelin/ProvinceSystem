# Batch 7.05 — Fixture harness + verify

**Plan + build:** One command writes all four MVP kinds to an output dir; green checklist without Discord.

**Repo:** `Workspace/armourshop`

**Depends on:** [04-grip-templates](./04-grip-templates.md)

## Plan

1. Add harness (`PackHarnessMain`):
   - Writes `armor_set`, `item`, `handheld`, and `large_handheld` ×3 grips into `tfmc_submissions`
   - Output: optional contents path arg (default `ItemsAdder Copy/.../contents`)
2. Assert YAML markers + expected PNG/model files; exit 1 on failure.
3. Document run command below.

## Build

| File | Action |
|------|--------|
| `pack/PackHarnessMain.java` | create — write all kinds + assert |
| Older `*FixtureMain` classes | leave (still call writers directly) |

## Verify

```bash
cd Workspace/armourshop
mvn -DskipTests package
java -cp target/classes net.tfminecraft.ArmourShop.pack.PackHarnessMain
```

Optional contents path:

```bash
java -cp target/classes net.tfminecraft.ArmourShop.pack.PackHarnessMain "D:/path/to/ItemsAdder/contents"
```

- [x] Armor YAML + 6 textures  
- [x] Item + handheld: `generate: true`, no custom model files  
- [x] Large: `generate: false`, thin model + grip parent  

## Out of scope

Plugin poll; LP; IA reload on live server.
