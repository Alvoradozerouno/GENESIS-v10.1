#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start GENESIS v10.1 API server on port 8080.
    Kills any existing process on that port first.

.USAGE
    # Default dev key:
    .\scripts\start_api.ps1

    # Custom keys:
    $env:GENESIS_API_KEY   = "my-secure-key"
    $env:GENESIS_ADMIN_KEY = "my-admin-key"
    .\scripts\start_api.ps1
#>

$ErrorActionPreference = "SilentlyContinue"
$Port       = 8080
$ScriptRoot = Split-Path $PSScriptRoot -Parent
$Uvicorn    = Join-Path $ScriptRoot ".venv\Scripts\uvicorn.exe"

# ── Kill any process already bound to port 8080 ─────────────────────────────
$pid8080 = (Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
            Select-Object -ExpandProperty OwningProcess -First 1)
if ($pid8080) {
    Stop-Process -Id $pid8080 -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 600
    Write-Host "  Killed old process (PID $pid8080) on :$Port"
}

# ── Verify uvicorn exists ────────────────────────────────────────────────────
if (-not (Test-Path $Uvicorn)) {
    Write-Host "ERROR: uvicorn not found at $Uvicorn"
    Write-Host "Run: python -m venv .venv && .venv\Scripts\pip install -r requirements.txt"
    exit 1
}

# ── Set default keys if not already set ─────────────────────────────────────
if (-not $env:GENESIS_API_KEY)   { $env:GENESIS_API_KEY   = "genesis-dev-key" }
if (-not $env:GENESIS_ADMIN_KEY) { $env:GENESIS_ADMIN_KEY = "genesis-admin-key" }

Write-Host ""
Write-Host "  GENESIS v10.1 API"
Write-Host "  Docs:    http://localhost:$Port/docs"
Write-Host "  Health:  http://localhost:$Port/api/health"
Write-Host "  Metrics: http://localhost:$Port/metrics"
Write-Host "  Key:     $env:GENESIS_API_KEY"
Write-Host ""

Set-Location $ScriptRoot
& $Uvicorn genesis_api:app --port $Port --host 0.0.0.0
