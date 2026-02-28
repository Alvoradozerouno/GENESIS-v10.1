#!/usr/bin/env pwsh
# GENESIS v10.1 — Local AI (llama.cpp) Server Startup
# Runs Qwen2.5-0.5B-Instruct on RTX 3060 via Vulkan
# Listens on http://localhost:8090 with OpenAI-compatible API
#
# Usage: .\scripts\start_llama.ps1
# Dashboard will read explanations from http://localhost:8090/v1/chat/completions

$ROOT   = Split-Path $PSScriptRoot -Parent
$MODEL  = Join-Path $ROOT "models\qwen2.5-0.5b-instruct-q4_k_m.gguf"
$PORT   = 8090
$LAYERS = 35    # GPU layers — all layers on RTX 3060 (6GB VRAM)
$CTX    = 2048  # Context window

if (-not (Test-Path $MODEL)) {
    Write-Host "ERROR: Model not found at $MODEL" -ForegroundColor Red
    Write-Host ""
    Write-Host "Download it with:" -ForegroundColor Yellow
    Write-Host '  $dest = "' + $MODEL + '"'
    Write-Host '  Start-BitsTransfer -Source "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf" -Destination $dest'
    exit 1
}

# Kill existing llama-server on port 8090
$existing = Get-NetTCPConnection -LocalPort $PORT -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
if ($existing) {
    Stop-Process -Id $existing -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
    Write-Host "Stopped existing llama-server on port $PORT"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GENESIS Local AI — Qwen2.5-0.5B"     -ForegroundColor Cyan
Write-Host "  GPU: RTX 3060 Laptop (Vulkan)"         -ForegroundColor Cyan
Write-Host "  Port: http://localhost:$PORT"           -ForegroundColor Cyan
Write-Host "  Model: $(Split-Path $MODEL -Leaf)"     -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

llama-server `
    --model $MODEL `
    --port $PORT `
    --host 0.0.0.0 `
    --n-gpu-layers $LAYERS `
    --ctx-size $CTX `
    --threads 8 `
    --parallel 4 `
    --log-disable
