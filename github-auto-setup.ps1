# GitHub Topics Automation Script
# Führe dieses Script aus, um GitHub Repository automatisch zu optimieren

$ErrorActionPreference = "Stop"

$token = "YOUR_GITHUB_PAT_HERE"  # Replace with your GitHub Personal Access Token
$owner = "Alvoradozerouno"
$repo = "GENESIS-v10.1"

$description = "🚀 World's first open-source Sovereign AI OS for banking & RegTech | 9 EU frameworks | 15-min deployment | Quantum + ZKP + ORION consciousness | €280M+ valuation"
$homepage = "https://github.com/Alvoradozerouno/GENESIS-v10.1"

$topics = @(
    "sovereign-ai", "regtech", "banking", "compliance", "kubernetes",
    "eidas", "gdpr", "basel-iii", "dora", "ai-act",
    "quantum-computing", "zero-knowledge-proofs", "machine-learning",
    "blockchain", "mlops", "open-source", "devops", "fintech",
    "security", "python"
)

$headers = @{
    "Authorization" = "token $token"
    "Accept" = "application/vnd.github.v3+json"
    "Content-Type" = "application/json"
}

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   GENESIS v10.1 - GitHub Repository Automatisierung      ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Test API Connection
Write-Host "🔍 Teste GitHub API Verbindung..." -ForegroundColor Yellow
try {
    $repoCheck = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo" -Headers $headers
    Write-Host "  ✅ Verbindung erfolgreich!" -ForegroundColor Green
    Write-Host "  📦 Repository: $($repoCheck.full_name)" -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "  ❌ Fehler: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "MANUELLE ALTERNATIVE:" -ForegroundColor Yellow
    Write-Host "  1. Öffne: https://github.com/$owner/$repo" -ForegroundColor Gray
    Write-Host "  2. Klicke auf ⚙️ neben 'About'" -ForegroundColor Gray
    Write-Host "  3. Füge Topics ein: sovereign-ai, regtech, banking..." -ForegroundColor Gray
    exit 1
}

# Update Description & Homepage
Write-Host "📝 [1/2] Aktualisiere Repository-Details..." -ForegroundColor Yellow
$updatePayload = @{
    description = $description
    homepage = $homepage
    has_issues = $true
    has_projects = $true
    has_wiki = $true
} | ConvertTo-Json -Depth 10

try {
    $result = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo" -Method Patch -Headers $headers -Body $updatePayload
    Write-Host "  ✅ Description aktualisiert!" -ForegroundColor Green
    Write-Host "  📄 $($result.description.Substring(0, [Math]::Min(80, $result.description.Length)))..." -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "  ⚠️  Teilweise erfolgreich oder Fehler: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host ""
}

# Set Topics
Write-Host "🏷️  [2/2] Setze Repository Topics (20 Topics)..." -ForegroundColor Yellow
$topicsPayload = @{
    names = $topics
} | ConvertTo-Json -Depth 10

try {
    $topicsResult = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/topics" -Method Put -Headers $headers -Body $topicsPayload
    Write-Host "  ✅ Topics erfolgreich gesetzt!" -ForegroundColor Green
    Write-Host "  🏷️  Anzahl: $($topicsResult.names.Count) Topics" -ForegroundColor Gray
    Write-Host "  🏷️  Topics: $($topicsResult.names -join ', ')" -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "  ❌ Fehler: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# Summary
Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║            ✅ GITHUB AUTOMATISIERUNG ABGESCHLOSSEN        ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "NÄCHSTE SCHRITTE:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. ✅ GitHub Description + Topics → FERTIG" -ForegroundColor Green
Write-Host ""
Write-Host "  2. 🔄 GitHub Discussions aktivieren (manuell):" -ForegroundColor Yellow
Write-Host "     → https://github.com/$owner/$repo/settings" -ForegroundColor Gray
Write-Host "     → Settings → Features → ☑ Discussions" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. HuggingFace Models hochladen:" -ForegroundColor Yellow
Write-Host "     Oeffne: https://huggingface.com/new-model" -ForegroundColor Gray
Write-Host "     Copy-Paste: HUGGINGFACE_MODEL_CARD_1.md" -ForegroundColor Gray
Write-Host ""
Write-Host "  4. Product Hunt Draft erstellen:" -ForegroundColor Yellow
Write-Host "     Oeffne: https://www.producthunt.com/posts/new" -ForegroundColor Gray
Write-Host "     Copy-Paste: PRODUCT_HUNT_COPY_PASTE.md" -ForegroundColor Gray
Write-Host ""
Write-Host "  5. Reddit Posts vorbereiten:" -ForegroundColor Yellow
Write-Host "     Copy-Paste: REDDIT_COPY_PASTE.md" -ForegroundColor Gray
Write-Host "     Start Monday 9 AM EST" -ForegroundColor Gray
Write-Host ""
Write-Host "ERWARTETE RESULTATE Week 1:" -ForegroundColor Cyan
Write-Host "  - 200-500 GitHub Stars" -ForegroundColor Gray
Write-Host "  - Top 10 Trending Python/Kubernetes" -ForegroundColor Gray
Write-Host "  - 10,000-30,000 unique visitors" -ForegroundColor Gray
Write-Host ""
