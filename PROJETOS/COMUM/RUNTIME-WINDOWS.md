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

- Para o indice de projetos, preferir a superficie canonica da Fabrica no repo
  irmao:
  - `..\fabrica\bin\ensure-fabrica-projects-index-runtime.ps1`
  - `python ..\fabrica\scripts\fabrica.py --repo-root . sync`
  - `..\fabrica\bin\apply-fabrica-projects-pg-schema.ps1`
  - `..\fabrica\bin\bootstrap-fabrica-projects-postgres.ps1`
- **Git Bash** continua opcional para os restantes `bin/*.sh`: tipicamente
  `C:\Program Files\Git\bin\bash.exe`.
- A partir do `npbb`, aponte explicitamente para o repo irmao `..\fabrica\`.

## Postgres / `host.env`

- Configuracao local: `~/.config/nemoclaw-host/host.env` (fora do Git).
- Variaveis: ver `SPEC-RUNTIME-POSTGRES-MATRIX.md` e `config/host.env.example`.
- Durante a migracao local no Windows, os wrappers `.ps1` do indice aceitam
  `host.env` com chaves legadas do namespace anterior e remapeiam esses
  valores para `FABRICA_*` apenas no processo atual.
