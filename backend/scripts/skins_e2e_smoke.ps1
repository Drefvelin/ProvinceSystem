# Skins API E2E smoke (Step 2). Run from backend/:
#   .\scripts\skins_e2e_smoke.ps1

$ErrorActionPreference = "Stop"
$BackendRoot = Split-Path -Parent $PSScriptRoot
Set-Location $BackendRoot
$env:SKINS_DEV = "1"

Write-Host "Running skins_e2e_smoke.py from $BackendRoot"
python scripts/skins_e2e_smoke.py
exit $LASTEXITCODE
