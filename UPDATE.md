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

Notes:

- `reset --hard` drops local edits (including chmod dirtiness). Always `chmod +x` again after.
- Branch is `tfmc-bot` — change the two `tfmc-bot` lines if staging tracks another branch.
- Does **not** update the Paper ArmourShop jar; copy that onto the MC server separately when needed.
