#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
COMPOSE=(docker compose -f docker-compose.staging.yml)

"${COMPOSE[@]}" up -d --build

for _ in $(seq 1 30); do
  if curl -sf http://127.0.0.1:18001/ping >/dev/null; then
    echo "Staging up: API http://127.0.0.1:18001  UI http://127.0.0.1:13001"
    echo "Ping: curl -s http://127.0.0.1:18001/ping"
    exit 0
  fi
  sleep 1
done

echo "ERROR: backend did not respond on :18001 within 30s" >&2
"${COMPOSE[@]}" ps
"${COMPOSE[@]}" logs --tail=80 backend
exit 1
