# GitHub Repository Auto-Setup - Simple Version
# No emojis, no special characters, just API calls

$token = "YOUR_GITHUB_PAT_HERE"  # Replace with your GitHub Personal Access Token
$owner = "Alvoradozerouno"
$repo = "GENESIS-v10.1"

$description = "World's first open-source Sovereign AI OS for banking and RegTech - 9 EU frameworks - 15-min deployment - Quantum + ZKP + ORION consciousness - 280M+ EUR valuation"
$topics = @("sovereign-ai", "regtech", "banking", "compliance", "kubernetes", "eidas", "gdpr", "basel-iii", "dora", "ai-act", "quantum-computing", "zero-knowledge-proofs", "machine-learning", "blockchain", "mlops", "open-source", "devops", "fintech", "security", "python")

$headers = @{
    "Authorization" = "token $token"
    "Accept" = "application/vnd.github.v3+json"
    "Content-Type" = "application/json"
}

Write-Host "=== GitHub Repository Automation ===" -ForegroundColor Cyan
Write-Host

Write-Host "[1/2] Setting Description..." -ForegroundColor Yellow
$body1 = @{ description = $description; homepage = "https://github.com/Alvoradozerouno/GENESIS-v10.1" } | ConvertTo-Json
try {
    Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo" -Method Patch -Headers $headers -Body $body1 | Out-Null
    Write-Host "SUCCESS: Description updated!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "[2/2] Setting Topics..." -ForegroundColor Yellow
$body2 = @{ names = $topics } | ConvertTo-Json
try {
    $result = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/topics" -Method Put -Headers $headers -Body $body2
    Write-Host "SUCCESS: $($result.names.Count) topics set!" -ForegroundColor Green
    Write-Host "Topics: $($result.names -join ', ')" -ForegroundColor Gray
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host
Write-Host "=== DONE ===" -ForegroundColor Green
Write-Host "Check: https://github.com/$owner/$repo" -ForegroundColor Cyan
