#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose -f docker-compose.staging.yml up -d --build
echo "Staging up: API http://127.0.0.1:18001  UI http://127.0.0.1:13001"
echo "Ping: curl -s http://127.0.0.1:18001/ping"
