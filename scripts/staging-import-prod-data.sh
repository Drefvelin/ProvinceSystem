#!/usr/bin/env bash
# Copy production ProvinceSystem data into this staging clone, optionally retag to dev.
#
# Usage:
#   ./scripts/staging-import-prod-data.sh /path/to/prod/backend/src/data
#   ./scripts/staging-import-prod-data.sh /path/to/prod/backend/src/data --to-realm dev
#
# If prod and staging are the same repo (shared backend/src/data), skip the copy and
# only run: ./scripts/staging-down.sh && python scripts/retag-realm.py --from main --to dev
set -euo pipefail
cd "$(dirname "$0")/.."

SRC="${1:-}"
if [[ -z "$SRC" || ! -d "$SRC" ]]; then
  echo "Usage: $0 /path/to/prod/backend/src/data [--to-realm dev]" >&2
  exit 1
fi
shift || true

TO_REALM=""
if [[ "${1:-}" == "--to-realm" ]]; then
  TO_REALM="${2:-}"
  if [[ -z "$TO_REALM" ]]; then
    echo "Missing realm after --to-realm" >&2
    exit 1
  fi
fi

./scripts/staging-down.sh

DEST="backend/src/data"
BACKUP="${DEST}.bak.$(date +%Y%m%d%H%M%S)"
if [[ -d "$DEST" ]]; then
  cp -a "$DEST" "$BACKUP"
  echo "Backed up staging data to $BACKUP"
fi

rsync -a --delete "${SRC}/" "${DEST}/"
echo "Copied ${SRC} -> ${DEST}"

if [[ -n "$TO_REALM" ]]; then
  python3 scripts/retag-realm.py --from main --to "$TO_REALM"
fi

./scripts/staging-up.sh
