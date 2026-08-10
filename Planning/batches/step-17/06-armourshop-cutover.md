# Step 17.06 — ArmourShop cutover

**Plan + build:** ArmourShop stops owning Discord link, notice poll, and player token mint; keeps pack apply + shop + admin code tools.

## Remove vs keep

| Remove from ArmourShop | Keep on ArmourShop |
|------------------------|--------------------|
| `/linkdiscord`, `/unlinkdiscord` | Shop UI, Categories, LP grants |
| `PluginNoticePoller` | Pack pull / apply / delete HTTP |
| Player `/armourshop token create` | `skins-api` + `pack-apply` config |
| Client: link/unlink/notices/`issueSkinsCode` | Admin `listtokens` / `token delete` |

**TFMCWeb** is sole owner of link, notices, Survival gate, `/token create skin|character`.

`/armourshop token create` replies: use `/token create skin` (TFMCWeb).

## LP (ops)

Grant `tfmcweb.token.create` on ranks that had `armourshop.token.create`. Remove the old AS token-create node from groups when convenient.

Survival servers need the **TFMCWeb** jar (AS softdepends it; warns if missing).

## Verify

1. `/linkdiscord` and `/token create skin` only via TFMCWeb.
2. `/armourshop pack pull` still works.
3. Admin `listtokens` / `token delete` still on AS.
4. Build ArmourShop jar; no leftover link/notice classes.

## Done when

Server runs with TFMCWeb + ArmourShop; link/token only on TFMCWeb; skins apply still green.

**Depends on:** [05-token-scopes](./05-token-scopes.md).
