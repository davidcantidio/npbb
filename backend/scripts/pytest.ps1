Param(
    [string[]]$PytestArgs = @()
)

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
Set-Location $repoRoot

$python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Error "Python nao encontrado em .venv. Crie o venv e instale as dependencias."
    exit 1
}

& $python -m pytest @PytestArgs
exit $LASTEXITCODE
