# Staging stack (AMP host / SSH)

Temporary ProvinceSystem next to production for Discord bot testing. Uses ports **18001** (API) and **13001** (UI). Production `docker-compose.yml` (8000/3000) is unchanged.

(If an older doc said 8001: that port is often already in use on the host.)

Data lives only under this clone (`backend/src/data`, etc.).

## Prerequisites

- Docker + Docker Compose on the host
- Git access to this repo

## Start (SSH)

```bash
git clone <ProvinceSystem-git-url> ~/tfmc-staging
cd ~/tfmc-staging   # or ~/ProvinceSystem if that is your staging clone
git pull
chmod +x scripts/staging-*.sh
./scripts/staging-down.sh   # clear a failed partial up
./scripts/staging-up.sh
curl -s http://127.0.0.1:18001/ping
```

Expected ping body: `{"ok":true}` (JSON). An HTML 404 means something else owns that port.

Stop later:

```bash
./scripts/staging-down.sh
```

## Red bot (`skinsreview` config.yml)

On the same machine as AMP/Red:

```yaml
api_base_url: "http://127.0.0.1:18001"
staff_key: "dev-staff-key"
bot_feed_channel_id: YOUR_BOT_FEED_CHANNEL_ID
poll_interval_seconds: 60
```

Then in Discord: `-reload skinsreview` → `/skinsreview ping`.

## Mint a code + submit a skin

Issue a code against staging:

```bash
curl -s -X POST http://127.0.0.1:18001/skins/codes \
  -H "Content-Type: application/json" \
  -H "X-Plugin-Key: dev-plugin-key" \
  -d '{"player_uuid":"00000000-0000-0000-0000-000000000001"}'
```

**Browser UI from your PC** (tunnel both ports):

```bash
ssh -L 13001:127.0.0.1:13001 -L 18001:127.0.0.1:18001 user@amp-host
```

Open `http://127.0.0.1:13001/skins`, redeem the code, upload, wait for `#bot-feed` (or `/skinsreview post <id>`).

## Keys (compose defaults)

| Env | Value |
|-----|--------|
| `SKINS_DEV` | `1` |
| `STAFF_KEY` | `dev-staff-key` |
| `PLUGIN_KEY` | `dev-plugin-key` |

Override in `docker-compose.staging.yml` if you want stronger keys for a longer-lived staging box.

## Port already in use?

```bash
sudo ss -tlnp | grep -E '18001|13001|8001'
```

Change the left-hand side of `ports:` in `docker-compose.staging.yml` if needed, keep container ports `8000` / `3000`.
