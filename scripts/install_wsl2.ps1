#!/usr/bin/env pwsh
# GENESIS v10.1 — WSL2 + Ubuntu 24.04 installer
# Run this as Administrator (right-click → Run as Administrator)
# After install, reboot once, then run: wsl --set-default-version 2

#Requires -RunAsAdministrator

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  GENESIS — WSL2 + Ubuntu 24.04 Install"  -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Enable WSL and Virtual Machine Platform features
Write-Host "1. Enabling Windows Subsystem for Linux..." -ForegroundColor Cyan
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart | Out-Null

Write-Host "2. Enabling Virtual Machine Platform..." -ForegroundColor Cyan
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart | Out-Null

Write-Host "3. Installing WSL2 kernel update..." -ForegroundColor Cyan
wsl --update --no-launch 2>&1 | Write-Host

Write-Host "4. Setting WSL2 as default..." -ForegroundColor Cyan
wsl --set-default-version 2

Write-Host "5. Installing Ubuntu 24.04..." -ForegroundColor Cyan
wsl --install -d Ubuntu-24.04 --no-launch

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  DONE — Please REBOOT your machine"     -ForegroundColor Green
Write-Host "  After reboot run: wsl -d Ubuntu-24.04"  -ForegroundColor Cyan
Write-Host "  Then: cd /mnt/c/Users/annah/..."        -ForegroundColor Cyan
Write-Host "  To enable full K8s: run genesis_v10.1.sh"  -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
