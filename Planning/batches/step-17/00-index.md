# Step 17 — TFMCWeb identity + Discord gate

**Repos:** `Workspace/tfmcweb/` (new) · `ProvinceSystem` · `tfmc_bot` · `Workspace/rpcharacters` · later migrate `armourshop`  
**Depends on:** Discord link exists ([step-5](../step-5/00-index.md)); skins tokens exist ([step-6](../step-6/00-index.md))  
**Playbook:** [13-tfmcweb.md](../../13-tfmcweb.md)

## Goal

Stand up **TFMCWeb** as the single Minecraft ↔ website bridge for **identity** (Discord link, guild grace, no alts), **scoped tokens**, and the **Survival Discord freeze gate** via RPCharacters — without building the character creator UI yet.

## Locked rules (from 13)

| Piece | Choice |
|-------|--------|
| Gate mode | **Survival only** — staff/helpers outside Survival are not gated |
| Leave Discord | **1 hour grace**; rejoin clears grace; expiry → unlink + freeze |
| Freeze | RPCharacters new reason; **do not** touch characters |
| Alts | One Discord ↔ one UUID |
| Commands | `/token create skin\|character`, `/linkdiscord`; admin `/web`; `/warning` |
| Bans | Essentials keeps execution; TFMCWeb + minecraftban poller mirror to Discord |

## Suggested build order (next step first)

### Do this first (unblocks everything)

1. **[01-rpc-discord-freeze](./01-rpc-discord-freeze.md)** — RPCharacters: `FreezeReason.DISCORD_REQUIRED` + public `setDiscordGate` / `reevaluateFreeze` (Survival-only already matches existing freeze skip for non-Survival).
2. **[02-identity-api](./02-identity-api.md)** — ProvinceSystem: extract/alias identity routes; `grace_until`; guild left/joined; status GET; notices; no-alts unchanged.
3. **[03-bot-guild-events](./03-bot-guild-events.md)** — `tfmc_bot`: `on_member_remove` / `on_member_join` → identity API.
4. **[04-tfmcweb-scaffold](./04-tfmcweb-scaffold.md)** — New plugin: config (API URL, plugin key), HTTP client, link cache, `/linkdiscord`, notice poller, Survival gate ↔ RPC.
5. **[05-token-scopes](./05-token-scopes.md)** — `/token create skin` (migrate from ArmourShop) + stub `character` scope on API.
6. **[06-armourshop-cutover](./06-armourshop-cutover.md)** — Remove link/notice/HTTP identity from ArmourShop; skins apply stays.
7. **[07-warn-and-ban-mirror](./07-warn-and-ban-mirror.md)** — `/warning` + Essentials ban → bot (after gate is live).
8. **[08-docs-verify](./08-docs-verify.md)** — Staging checklist.

**Immediate next action:** implement batch **01** (RPC freeze API) in parallel with **02** (identity grace API) — neither needs the full TFMCWeb jar yet; TFMCWeb scaffold (**04**) consumes both.

## Out of this step

- Character creator website / RPCharacters creation rewrite  
- Folding SimpleFactions HTTP into TFMCWeb (follow-on)  
- Replacing Essentials with another ban plugin  

## Checkpoint

```text
RPC freeze API → identity+grace API → bot leave/join → TFMCWeb scaffold+gate
  → token scopes → ArmourShop cutover → warn/ban mirror → verify
```

**Done when:** Survival player unlinked (or past 1h leave grace) is frozen; rejoin Discord within 1h does not freeze; staff non-Survival unaffected; `/linkdiscord` and `/token create skin` work from TFMCWeb; ArmourShop no longer owns link.

## Status

**17.01–17.08 done** (docs + staging checklist written). Humans tick staging boxes on the live server — do not invent green ticks. Character creator UI remains out of scope.
