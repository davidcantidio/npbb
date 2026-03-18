---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F3-04-002-Materializar-artefatos-Markdown-e-estado-de-sincronizacao"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-1 - Materializar artefatos Markdown e status de sync

## objetivo

escrever artefatos canonicos e expor o estado de sincronizacao do projeto

## precondicoes

- `ISSUE-F1-02-001` concluida
- `ISSUE-F3-03-002` concluida

## arquivos_a_ler_ou_tocar

- `backend/app/services/framework_orchestrator.py`
- `backend/app/schemas/framework.py`
- `backend/tests/test_framework_markdown_sync.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir lista de arquivos escritos e status de sincronizacao
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_markdown_sync.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_markdown_sync.py`

## resultado_esperado

Artefatos canonicos gerados com status de sync observavel.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_markdown_sync.py`

## stop_conditions

- parar se a escrita em filesystem colidir com a politica de precedencia aprovada
