#!/usr/bin/env pwsh
# GENESIS v10.1 — Master Startup
# Starts: GENESIS API (port 8080) + Local AI / llama-server (port 8090)
#
# Usage: .\START_GENESIS.ps1
# Dashboard: open ui/index.html in browser

$ROOT   = $PSScriptRoot
$VENV   = Join-Path $ROOT ".venv\Scripts"
$MODEL  = Join-Path $ROOT "models\qwen2.5-0.5b-instruct-q4_k_m.gguf"
$env:PATH += ";$env:USERPROFILE\.local\bin"

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  GENESIS v10.1 - Sovereign AI OS"               -ForegroundColor Cyan
Write-Host "  RTX 3060 | 9 EU Frameworks | R2=0.8955"         -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# ── Kill existing processes ───────────────────────────────────
foreach ($port in @(8080, 8090)) {
    $pid = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
           Select-Object -ExpandProperty OwningProcess
    if ($pid) {
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        Write-Host "  Cleared port $port"
    }
}
Start-Sleep -Seconds 1

# ── Start GENESIS API ─────────────────────────────────────────
Write-Host "[ 1/2 ] Starting GENESIS API on :8080..." -ForegroundColor Green
$apiProc = Start-Process -FilePath "$VENV\uvicorn.exe" `
    -ArgumentList "genesis_api:app --port 8080 --host 0.0.0.0 --log-level warning" `
    -WorkingDirectory $ROOT `
    -PassThru -WindowStyle Minimized
Write-Host "        PID $($apiProc.Id) | http://localhost:8080/docs"

# ── Start llama-server (if model exists) ─────────────────────
if (Test-Path $MODEL) {
    Write-Host "[ 2/2 ] Starting Local AI (Qwen2.5-0.5B) on :8090..." -ForegroundColor Magenta
    $aiProc = Start-Process -FilePath "llama-server" `
        -ArgumentList "--model `"$MODEL`" --port 8090 --host 0.0.0.0 --n-gpu-layers 35 --ctx-size 2048 --threads 8 --parallel 4 --log-disable" `
        -PassThru -WindowStyle Minimized
    Write-Host "        PID $($aiProc.Id) | http://localhost:8090"
} else {
    Write-Host "[ 2/2 ] Model not ready yet — check download progress:" -ForegroundColor Yellow
    Write-Host "        Get-BitsTransfer | Select DisplayName,@{N='%';E={[math]::Round(`$_.BytesTransferred/`$_.BytesTotal*100,1)}}"
}

# ── Wait + verify ─────────────────────────────────────────────
Write-Host ""
Write-Host "Waiting for services..." -ForegroundColor Gray
Start-Sleep -Seconds 5

try {
    $h = Invoke-RestMethod "http://localhost:8080/api/health" -TimeoutSec 5
    $ai = if ($h.local_ai_ready) { "ONLINE" } else { "starting..." }
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "  STATUS: $($h.status.ToUpper())"                 -ForegroundColor Green
    Write-Host "  Risk Engine R2: $($h.model_r2)"                 -ForegroundColor White
    Write-Host "  Frameworks: $($h.frameworks_loaded)"            -ForegroundColor White
    Write-Host "  Local AI: $ai"                                  -ForegroundColor $(if($h.local_ai_ready){'Green'}else{'Yellow'})
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  API Docs:  http://localhost:8080/docs"          -ForegroundColor Cyan
    Write-Host "  Dashboard: open ui/index.html in browser"       -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
} catch {
    Write-Host "  API health check failed — check logs" -ForegroundColor Red
}
Write-Host ""
