# Generate self-signed TLS certificate for local HTTPS
# Run once: .\scripts\gen_cert.ps1
# For production: replace certs/genesis.crt + certs/genesis.key with real cert (Let's Encrypt / internal CA)

$certDir = Join-Path $PSScriptRoot "..\nginx\certs"
New-Item -ItemType Directory -Force -Path $certDir | Out-Null

$crt = Join-Path $certDir "genesis.crt"
$key = Join-Path $certDir "genesis.key"

if (Test-Path $crt) {
    Write-Host "Certificate already exists at $crt — skipping."
    exit 0
}

# Try openssl (available in Git for Windows / WSL / OpenSSL)
$openssl = Get-Command openssl -ErrorAction SilentlyContinue
if ($openssl) {
    & openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes `
        -keyout $key -out $crt `
        -subj "/CN=genesis.local/O=GENESIS/C=AT" `
        -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
    Write-Host "✅ Certificate generated: $crt"
} else {
    # Fallback: PowerShell New-SelfSignedCertificate (Windows only)
    $cert = New-SelfSignedCertificate `
        -DnsName "localhost","genesis.local" `
        -CertStoreLocation "Cert:\CurrentUser\My" `
        -NotAfter (Get-Date).AddYears(10) `
        -KeyAlgorithm RSA -KeyLength 4096

    # Export PFX then convert
    $pfx = Join-Path $certDir "genesis.pfx"
    $pwd = ConvertTo-SecureString -String "genesis" -Force -AsPlainText
    Export-PfxCertificate -Cert $cert -FilePath $pfx -Password $pwd | Out-Null

    Write-Host "✅ PFX exported to $pfx (password: genesis)"
    Write-Host "   Convert to PEM with openssl or use nginx ssl_certificate_pfx (njs required)."
    Write-Host "   Recommended: install Git for Windows (includes openssl) then re-run this script."
}
