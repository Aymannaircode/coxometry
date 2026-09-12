# Demo launch — Coxométrie backend with V5 Phase 2 (16 landmarks + IT).
#
# Use this script for demos / jury presentations.
# Compatibility default in code remains V2 when MODEL_VERSION is unset.
#
# Usage (from anywhere):
#   .\backend\run_demo.ps1
#   .\backend\run_demo.ps1 -Port 8001
#
# Verify after start:
#   GET http://127.0.0.1:<port>/health  → model_version must be "v5_phase2"

param(
    [int]$Port = 8001,
    [string]$HostAddress = "0.0.0.0"
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$env:MODEL_VERSION = "v5_phase2"

Write-Host "=== Coxométrie DEMO backend ===" -ForegroundColor Cyan
Write-Host "MODEL_VERSION = $env:MODEL_VERSION"
Write-Host "Host          = $HostAddress"
Write-Host "Port          = $Port"
Write-Host "Health check  = http://127.0.0.1:$Port/health"
Write-Host "OpenAPI       = http://127.0.0.1:$Port/docs"
Write-Host ""
Write-Host "Expected health.model_version: v5_phase2" -ForegroundColor Yellow
Write-Host "Do NOT use bare uvicorn without MODEL_VERSION for a V5 demo." -ForegroundColor Yellow
Write-Host ""

$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    $Python = "python"
}

& $Python -m uvicorn backend.main:app --host $HostAddress --port $Port
