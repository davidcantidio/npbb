# Inicia o backend FastAPI com a venv em backend\.venv (Windows / PowerShell).
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$VenvPython = Join-Path $RepoRoot "backend\.venv\Scripts\python.exe"
$BackendEnv = Join-Path $RepoRoot "backend\.env"

if (-not (Test-Path -LiteralPath $BackendEnv)) {
    Write-Error "Arquivo backend\.env nao encontrado. Copie o exemplo e preencha o banco:`n  cd backend`n  Copy-Item .env.example .env`nEdite DATABASE_URL e DIRECT_URL (Supabase ou Postgres local)."
    exit 1
}

$dbUrlSet = $false
foreach ($line in Get-Content -LiteralPath $BackendEnv) {
    $t = $line.Trim()
    if ($t -eq "" -or $t.StartsWith("#")) { continue }
    if ($t -match '^\s*DATABASE_URL\s*=') {
        $val = ($t -split '=', 2)[1].Trim().Trim('"').Trim("'")
        if (-not [string]::IsNullOrWhiteSpace($val)) { $dbUrlSet = $true }
        break
    }
}
if (-not $dbUrlSet) {
    Write-Error "DATABASE_URL em backend\.env esta ausente ou vazia (igual ao .env.example). Preencha com a URI do Postgres (veja comentarios em backend\.env.example)."
    exit 1
}

if (-not (Test-Path -LiteralPath $VenvPython)) {
    Write-Error "Python da venv nao encontrado: $VenvPython`nCrie a venv: cd backend; python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt (ou equivalente)."
    exit 1
}

$pyVersion = & $VenvPython -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if ($pyVersion -ne "3.12") {
    Write-Error "Venv backend usa Python $pyVersion. Esperado Python 3.12."
    exit 1
}

$prefix = "${RepoRoot};${RepoRoot}\backend"
if ($env:PYTHONPATH) {
    $env:PYTHONPATH = "${prefix};${env:PYTHONPATH}"
} else {
    $env:PYTHONPATH = $prefix
}

$uvHost = if ($env:UVICORN_HOST) { $env:UVICORN_HOST } else { "127.0.0.1" }
$uvPort = if ($env:UVICORN_PORT) { $env:UVICORN_PORT } else { "8000" }

$portListeners = Get-NetTCPConnection -LocalPort ([int]$uvPort) -State Listen -ErrorAction SilentlyContinue
if ($portListeners) {
    $listenerPids = @($portListeners | Select-Object -ExpandProperty OwningProcess -Unique)
    $listenerDescriptions = @(
        foreach ($listenerPid in $listenerPids) {
            $proc = Get-CimInstance Win32_Process -Filter "ProcessId = $listenerPid" -ErrorAction SilentlyContinue
            if ($proc) {
                "PID ${listenerPid}: $($proc.CommandLine)"
            } else {
                "PID ${listenerPid}"
            }
        }
    )
    Write-Error ("Ja existe processo escutando em {0}:{1}. Finalize a instancia anterior antes de subir outro backend.`n{2}" -f $uvHost, $uvPort, ($listenerDescriptions -join "`n"))
    exit 1
}

Set-Location -LiteralPath $RepoRoot
Write-Host "Backend Python: $VenvPython"

$skipDbPreflight = $env:SKIP_DB_PREFLIGHT -and $env:SKIP_DB_PREFLIGHT.ToLower() -in @("1", "true", "yes")
if (-not $skipDbPreflight) {
    Write-Host "Verificando conectividade com o banco..."
    @'
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from app.db.database import engine, get_database_endpoint_info

try:
    with engine.connect() as connection:
        connection.execute(text('select 1'))
except OperationalError as exc:
    endpoint = get_database_endpoint_info()
    detail = str(getattr(exc, "orig", exc)).strip()
    print(f"ERRO: banco indisponivel para o backend dev. endpoint={endpoint}")
    print(detail)
    raise SystemExit(2)
else:
    print(f"Banco acessivel. endpoint={get_database_endpoint_info()}")
'@ | & $VenvPython -
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Falha no preflight do banco. Corrija DATABASE_URL/DIRECT_URL ou a conectividade de rede antes de subir a API. Se quiser ignorar esse check, defina SKIP_DB_PREFLIGHT=true."
        exit $LASTEXITCODE
    }
}

& $VenvPython -m uvicorn app.main:app --reload --app-dir backend --host $uvHost --port $uvPort
