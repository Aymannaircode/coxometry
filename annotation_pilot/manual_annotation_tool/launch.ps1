$ErrorActionPreference = "Stop"

$toolDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$server = Join-Path $toolDirectory "server.py"

Write-Host "Démarrage de l'outil d'annotation manuelle..."
Write-Host "Ouvrez ensuite http://127.0.0.1:8765 dans votre navigateur."
Write-Host "Aucune annotation n'est lancée automatiquement. Arrêt : Ctrl+C."

python $server
