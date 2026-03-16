Param(
    [string]$DirectUrl,
    [string]$DatabaseUrl,
    [switch]$StrictDirectUrl
)

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
Set-Location $repoRoot

if ($DirectUrl) {
    $env:DIRECT_URL = $DirectUrl
}
if ($DatabaseUrl) {
    $env:DATABASE_URL = $DatabaseUrl
}
if ($StrictDirectUrl) {
    $env:ALEMBIC_STRICT_DIRECT_URL = "true"
}

$hasDirectUrl = [bool]($env:DIRECT_URL)
$hasDatabaseUrl = [bool]($env:DATABASE_URL)
if ($StrictDirectUrl -and -not $hasDirectUrl) {
    Write-Error "ALEMBIC_STRICT_DIRECT_URL exige DIRECT_URL. Informe -DirectUrl ou configure DIRECT_URL."
    exit 1
}
if (-not ($hasDirectUrl -or $hasDatabaseUrl)) {
    Write-Error "DIRECT_URL ou DATABASE_URL precisam estar configuradas. Informe via ambiente ou parametros -DirectUrl / -DatabaseUrl."
    exit 1
}

$alembic = ".\.venv\Scripts\alembic.exe"
if (-not (Test-Path $alembic)) {
    Write-Error "Alembic não encontrado em .venv. Instale dependências e crie o venv antes."
    exit 1
}

& $alembic upgrade head
