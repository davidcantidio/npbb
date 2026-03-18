---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F1-01-001-Estabilizar-baseline-do-embriao-FRAMEWORK3"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-1 - Estabilizar boot e smoke do backend com router framework

## objetivo

restaurar o import de app.main com o router framework habilitado

## precondicoes

- ler o estado atual do embriao framework e reproduzir a regressao de import

## arquivos_a_ler_ou_tocar

- `backend/app/services/framework_orchestrator.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/app/main.py`
- `backend/tests/test_framework_startup.py`

## testes_red

- testes_a_escrever_primeiro:
  - reproduzir a falha de import causada por `app.core.config` inexistente
  - proteger o boot do backend com smoke test especifico do recorte framework
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_startup.py`
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -c "import app.main"`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_startup.py`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -c "import app.main"`

## resultado_esperado

app.main volta a importar com o router framework habilitado e a regressao atual fica encapsulada por smoke test.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_startup.py`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -c "import app.main"`

## stop_conditions

- parar se a correcao exigir criar um subsistema global novo de configuracao fora do escopo da issue
- parar se o import de `app.main` continuar quebrando por dependencia nao relacionada ao recorte framework
