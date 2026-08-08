# Staging update (redeploy)

SSH into the AMP host, `cd` into your staging clone yourself (`~/ProvinceSystem` or `~/tfmc-staging`), then paste:

```bash
git fetch origin
git checkout tfmc-bot
git reset --hard origin/tfmc-bot
chmod +x scripts/staging-*.sh
./scripts/staging-down.sh
./scripts/staging-up.sh
curl -s http://127.0.0.1:18001/ping
```

Expected ping: `{"ok":true}`.

## Browser from your PC (SSH tunnel)

From your machine (PowerShell / terminal), keep this session open:

```bash
ssh -L 13001:127.0.0.1:13001 -L 18001:127.0.0.1:18001 user@amp-host
```

Replace `user@amp-host` with your real SSH login.

Then open the website locally:

- UI: [http://127.0.0.1:13001](http://127.0.0.1:13001)
- Skins: [http://127.0.0.1:13001/skins](http://127.0.0.1:13001/skins)

(`13001` = Next UI, `18001` = API — both must be forwarded so the browser can call the API.)

Notes:

- `reset --hard` drops local edits (including chmod dirtiness). Always `chmod +x` again after.
- Branch is `tfmc-bot` — change the two `tfmc-bot` lines if staging tracks another branch.
- Does **not** update the Paper ArmourShop jar; copy that onto the MC server separately when needed.
