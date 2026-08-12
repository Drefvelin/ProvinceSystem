# Batch 27.01 — Planning lock (templates + resetkit)

**Plan + build:** Lock YAML shape and vocabulary in playbooks; no product code required beyond doc consistency.

**Repos:** Planning hubs  
**Depends on:** [00-index](./00-index.md)

## Locked YAML (illustrative)

```yaml
kits:
  starter:
    items:
      - path: m.tools.IRON_HUNTING_KNIFE
        amount: 1
        editable:
          skin-png: knife_skin
          base-set: knives
          2d-template: handheld
          3d-template: item_3d
```

| Key | Rule |
|-----|------|
| `2d-template` | Skin kind for flat upload; required on editable lines after this step |
| `3d-template` | Optional skin kind for 3D path; **absent** = 3D disallowed |
| `skin-png` / `base-set` | Unchanged |

## Staff command

```text
/rpcharacter resetkit <player> <character_id> <kit_id>
```

## Verify

- [x] [14-character-creator.md](../../14-character-creator.md) editable section shows templates + resetkit
- [x] This index locked table matches hubs

## Status

**Done** (27.01). Closed with [05-docs-verify](./05-docs-verify.md).
