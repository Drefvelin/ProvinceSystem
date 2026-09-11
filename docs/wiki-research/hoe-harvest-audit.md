# Hoe harvest-area audit

## MMOItems defaults

Primary source: `C:\Users\MSI\Desktop\plugins\MMOItems\item\tools.yml`.

| MMOItems ID | Bukkit material | Efficiency | Harvest lore | Default area |
|---|---|---:|---|---|
| `IRON_HOE` | `IRON_HOE` | II | none | 1 block |
| `STEEL_HOE` | `IRON_HOE` | III | Harvest I | 3x3 |
| `ABYSSALITE_HOE` | `DIAMOND_HOE` | IV | Harvest II | 5x5 |
| `MYTHRIL_HOE` | `NETHERITE_HOE` | V | Harvest III | 7x7 |

Exact definitions:

- Iron: lines 154-170; material line 156, Efficiency line 164, `disable-enchanting` line 166.
- Steel: lines 229-251; material line 231, Efficiency line 240, `disable-enchanting` line 244, lore line 251.
- Abyssalite: lines 310-331; material line 312, Efficiency line 320, `disable-enchanting` line 324, lore line 331.
- Mythril: lines 389-410; material line 391, Efficiency line 399, `disable-enchanting` line 403, lore line 410.

The configured `block-interaction-range` values at lines 161, 237, 317, and 396 are reach attributes, not harvest-area stats. None of these hoe definitions contains a mining, farming, or area stat. Because all four definitions disable enchanting, the built-in Efficiency levels above are the relevant default player-facing facts.

## FarmingUpgrade mapping and calculation

Primary config: `C:\Users\MSI\Desktop\plugins\FarmingUpgrade\config.yml`.

- `radiusPerEfficiencyLevel: 2.0`: lines 16-18.
- Tool matching is ordered, with the first matching filter used: lines 56-70.
- `IRON_HOE` base radius `-5.0`: lines 125-127.
- `DIAMOND_HOE` base radius `-6.0`: lines 128-130.
- `NETHERITE_HOE` base radius `-7.0`: lines 131-133.

The installed runtime artifact is `C:\Users\MSI\Desktop\plugins\farmingupgrade-1.7.2.jar`. `javap -c -p` inspection of `no.hyp.farmingupgrade.FarmingUpgradePlugin` and its nested `ToolUpgrade` class confirms:

1. `ToolUpgrade.toolType(...)` compares `ItemStack.getType()` with each configured material list and returns the first match. The active hoe entries have no lore, NBT, permission, or MMOItems-ID filter. The MMOItems Harvest lore therefore does not control this hook.
2. `calculateRadius(...)` computes `int(min(10.0, tool.radius + ItemStack.getEnchantmentLevel(Enchantment.DIG_SPEED) * radiusPerEfficiencyLevel))`.
3. `findAdjacentMaterials(...)` uses a grid side length of `2 * radius + 1`. For the negative Iron default radius, directional traversal is skipped and the clicked centre block is retained.

Applying the runtime formula to the MMOItems defaults:

- Iron: `-5 + 2 * 2 = -1` -> clicked block only.
- Steel: `-5 + 2 * 3 = 1` -> 3x3.
- Abyssalite: `-6 + 2 * 4 = 2` -> 5x5.
- Mythril: `-7 + 2 * 5 = 3` -> 7x7.

The previous Eff 0-V matrix was a valid hypothetical application of the material formula, but it obscured the actual configured per-item defaults requested for these four MMOItems hoes.
