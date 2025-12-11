Param(
    [string]$DatabaseUrl
)

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
Set-Location $repoRoot

if ($DatabaseUrl) {
    $env:DATABASE_URL = $DatabaseUrl
}

if (-not $env:DATABASE_URL) {
    Write-Error "DATABASE_URL não definido. Informe via ambiente ou parâmetro -DatabaseUrl."
    exit 1
}

$alembic = ".\.venv\Scripts\alembic.exe"
if (-not (Test-Path $alembic)) {
    Write-Error "Alembic não encontrado em .venv. Instale dependências e crie o venv antes."
    exit 1
}

& $alembic upgrade head
