$ErrorActionPreference = "Stop"

$toolDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$launchScript = Join-Path $toolDirectory "launch_new_26.ps1"
$port = 8765

Write-Host "Session de correction ASL/ASM - B26_25 et B26_26 uniquement."
Write-Host ""
Write-Host "Landmarks a corriger :"
Write-Host "  B26_25 : ASL_L (LM-06)"
Write-Host "  B26_26 : ASL_R (LM-05) et ASL_L (LM-06)"
Write-Host ""
Write-Host "URLs directes (apres demarrage) :"
Write-Host ('  http://127.0.0.1:' + $port + '/?pilot_id=B26_25&landmark=ASL_L')
Write-Host ('  http://127.0.0.1:' + $port + '/?pilot_id=B26_26&landmark=ASL_R')
Write-Host ""

& $launchScript --cases B26_25 B26_26
