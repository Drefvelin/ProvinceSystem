# Start ProvinceSystem API reachable from remote AMP (binds all interfaces).
# From backend/:  .\scripts\run_api_public.ps1
#
# Then open Windows Firewall for TCP 8000 (Private/Public as needed),
# put http://YOUR_PUBLIC_IP:8000 in skinsreview/config.yml on AMP.

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

if (-not $env:SKINS_DEV) { $env:SKINS_DEV = "1" }
if (-not $env:STAFF_KEY) { $env:STAFF_KEY = "dev-staff-key" }
if (-not $env:PLUGIN_KEY) { $env:PLUGIN_KEY = "dev-plugin-key" }

Write-Host "SKINS_DEV=$env:SKINS_DEV"
Write-Host "STAFF_KEY=$env:STAFF_KEY"
Write-Host "PLUGIN_KEY=$env:PLUGIN_KEY"
Write-Host "Listening on http://0.0.0.0:8000 (use your public IP in Discord bot config.yml)"
Write-Host "Ping check: curl http://127.0.0.1:8000/ping"

python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
