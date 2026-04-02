---
doc_id: "RUNTIME-WINDOWS.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-30"
---

# RUNTIME — Windows (OpenClaw repo)

Referencia unica para agentes no Windows: evita confusao entre `python3` do PATH,
interpretadores sem dependencias e o ambiente do projeto.

## Python e pytest

- **Raiz do repositorio OpenClaw:** pasta que contem `requirements.txt` e
  `scripts/run-pytest.ps1` (ver `AGENTS.md` na raiz desse repositorio).
- Usar o venv do projeto `.venv` nessa raiz quando existir.
- **Comando recomendado (Windows):** `scripts\run-pytest.ps1` com os mesmos
  argumentos que passaria ao pytest.
- **Alternativa:** `.venv\Scripts\python.exe -m pytest <args>`
- **Evitar:** `python3 -m pytest` quando o `python3` do PATH nao for o do venv
  (muitas vezes falta pytest).

Detalhe e precedencia: `AGENTS.md` na raiz do repositorio OpenClaw.

## Documentos relacionados

| Documento | Relacao |
|-----------|---------|
| `boot-prompt.md` | Nivel 1: leitura no Windows antes de pytest/shell |
| `SESSION-MAPA.md` | Aponta para este ficheiro na secao de indice operacional |
| `SPEC-RUNTIME-POSTGRES-MATRIX.md` | `host.env`, sync e variaveis Postgres |
| `GOV-FRAMEWORK-MASTER.md` | Secao 3 indexa este runbook |

## Bash e scripts em `bin/*.sh`

- Preferir **Git Bash**: tipicamente `C:\Program Files\Git\bin\bash.exe`.
- Correr scripts a partir da raiz do clone OpenClaw, por exemplo:
  `./bin/sync-fabrica-projects-db.sh`, `./bin/verify-openclaw-skill-parity.sh`.

## Postgres / `host.env`

- Configuracao local: `~/.config/nemoclaw-host/host.env` (fora do Git).
- Variaveis: ver `SPEC-RUNTIME-POSTGRES-MATRIX.md` e `config/host.env.example`.
