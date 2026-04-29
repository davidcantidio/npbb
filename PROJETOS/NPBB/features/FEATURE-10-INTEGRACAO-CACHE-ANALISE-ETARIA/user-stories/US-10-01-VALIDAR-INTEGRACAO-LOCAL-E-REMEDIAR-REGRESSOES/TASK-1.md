---
doc_id: "TASK-1.md"
user_story_id: "US-10-01-VALIDAR-INTEGRACAO-LOCAL-E-REMEDIAR-REGRESSOES"
task_id: "T1"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-27"
depends_on: []
parallel_safe: false
write_scope:
  - "PROJETOS/NPBB/features/FEATURE-10-INTEGRACAO-CACHE-ANALISE-ETARIA/**"
  - "artifacts/phase-f4/evidence/"
tdd_aplicavel: false
---

# T1 - Executar pre-voo, migration e startup limpo

## objetivo

Estabelecer baseline do workspace, aplicar a migration nova e provar que a API
e o worker sobem limpos antes de qualquer remediacao de codigo.

## precondicoes

- acesso ao repo com `backend/.env` configurado para banco real de dev/staging
- interpretador Python do backend disponivel conforme `AGENTS.md`
- frontend e backend com dependencias ja instaladas

## orquestracao

- `depends_on`: nenhuma
- `parallel_safe`: `false`
- `write_scope`: `governanca da FEATURE-10` e `artifacts/phase-f4/evidence/`

## arquivos_a_ler_ou_tocar

- `PLANO-INTEGRACAO-GERAL-CACHE-ANALISE-ETARIA.md`
- `docs/SETUP.md`
- `backend/alembic/versions/0c1d2e3f4a5b_create_dashboard_cache_versions.py`
- `artifacts/phase-f4/evidence/README.md`

## passos_atomicos

1. rodar `git status --short` e `git diff --stat` para registrar baseline
2. aplicar `alembic upgrade head` no backend
3. validar a existencia de `dashboard_cache_versions` no banco alvo
4. subir API e worker pelo script oficial do repo
5. validar `/health` e `/health/ready`
6. registrar comandos e resultados em `artifacts/phase-f4/evidence/`

## comandos_permitidos

- `git status --short`
- `git diff --stat`
- `cd backend && alembic upgrade head`
- `./scripts/dev_backend.sh`
- `curl -s http://127.0.0.1:8000/health`
- `curl -s http://127.0.0.1:8000/health/ready`

## resultado_esperado

Baseline do workspace registrado, migration aplicada, tabela validada e stack
local subindo limpa o suficiente para continuar nas tasks de backend e
frontend.

## testes_ou_validacoes_obrigatorias

- `git status --short`
- `git diff --stat`
- `cd backend && alembic upgrade head`
- validar consulta simples em `dashboard_cache_versions`
- `curl -s http://127.0.0.1:8000/health`
- `curl -s http://127.0.0.1:8000/health/ready`

## stop_conditions

- parar se a migration conflitar com schema existente
- parar se `DATABASE_URL` ou `DIRECT_URL` reais nao estiverem disponiveis
- parar se a stack nao subir por drift de ambiente nao relacionado ao cache
  etario e registrar a falha como `environment`
