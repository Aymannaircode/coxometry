$ErrorActionPreference = "Stop"

$toolDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$server = Join-Path $toolDirectory "server.py"
$prepareScript = Join-Path $toolDirectory "prepare_manual_annotation_new_26.py"
$projectRoot = Split-Path -Parent (Split-Path -Parent $toolDirectory)
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$port = 8765

if (-not (Test-Path $venvPython)) {
    Write-Error "Python du venv introuvable : $venvPython (requis pour pydicom/numpy/Pillow)."
}

function Stop-AllAnnotationServers {
    Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -like "*manual_annotation_tool*server.py*" } |
        ForEach-Object {
            Write-Host ("Arret du serveur d'annotation existant (PID {0})..." -f $_.ProcessId)
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        }
}

Stop-AllAnnotationServers
Start-Sleep -Seconds 1

Write-Host "Verification pre-annotation (verification_radios.csv, 26 DICOM)..."
& $venvPython -u $prepareScript
if ($LASTEXITCODE -ne 0) {
    Write-Error "Echec de la preparation - corriger avant de lancer l'outil."
}

Write-Host "Demarrage - lot bassin 26 DICOM (a_annoter)..."
Write-Host "Mode : new_26 | Port : $port"
Write-Host "Ouvrez http://127.0.0.1:$port dans votre navigateur."
Write-Host "Les DICOM originaux ne sont pas modifies ; PNG de cache pour affichage uniquement."
Write-Host "Arret : Ctrl+C"

$pythonArgs = @(
    $server
    "--dataset"
    "new_26"
    "--port"
    "$port"
)
if ($args.Count -gt 0) {
    $pythonArgs += $args
}

$commandLine = "$venvPython " + ($pythonArgs -join " ")
Write-Host "Commande : $commandLine"

Set-Location $projectRoot
& $venvPython -u @pythonArgs
