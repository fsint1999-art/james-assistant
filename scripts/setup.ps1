# Windows (PowerShell): cria o venv, instala dependências e compila o HUD.
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
python -m venv backend\.venv
& backend\.venv\Scripts\python.exe -m pip install -U pip
& backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
Push-Location frontend; npm install --no-audit --no-fund; npm run build; Pop-Location
$cfg = Join-Path $HOME ".config\james"; New-Item -ItemType Directory -Force $cfg | Out-Null
if (-not (Test-Path "$cfg\config.json")) { Copy-Item config.example.json "$cfg\config.json" }
Write-Host "Pronto. Edite $cfg\config.json e rode: .\scripts\run.ps1  ->  http://127.0.0.1:8765"
