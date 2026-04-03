# Ativa a venv do backend no PowerShell atual (python/pip passam a ser os da venv).
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$Activate = Join-Path $RepoRoot "backend\.venv\Scripts\Activate.ps1"

if (-not (Test-Path -LiteralPath $Activate)) {
    Write-Error "Activate.ps1 nao encontrado: $Activate`nCrie a venv: cd backend; python -m venv .venv"
    exit 1
}

. $Activate
Write-Host "Venv ativa: backend\.venv" -ForegroundColor Green
