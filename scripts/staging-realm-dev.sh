#!/usr/bin/env bash
# Pull latest site-rework, migrate old global DB, retag main -> dev, restart staging.
#
# Run on the AMP/staging host from the ProvinceSystem clone (e.g. ~/ProvinceSystem):
#   chmod +x scripts/staging-realm-dev.sh
#   ./scripts/staging-realm-dev.sh
#
# Safe to re-run only when target realm dev is empty (retag refuses if dev rows exist).
set -euo pipefail
cd "$(dirname "$0")/.."

git fetch origin
git checkout site-rework
git reset --hard origin/site-rework
chmod +x scripts/staging-*.sh

./scripts/staging-down.sh

echo "Migrating database (adds realm_id columns; old rows stay main)..."
(cd backend && python3 -c "from src.skins.db import migrate; migrate()")

echo "Retagging realm main -> dev..."
python3 scripts/retag-realm.py --from main --to dev

./scripts/staging-up.sh

echo -n "Ping: "
curl -s http://127.0.0.1:18001/ping
echo
