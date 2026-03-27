---
doc_id: "TASK-4.md"
user_story_id: "US-2-03-ROLLOUT-POR-EVENTO"
task_id: "T4"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - T3
parallel_safe: false
write_scope:
  - "backend/tests/"
tdd_aplicavel: true
---

# TASK-4 - Testes de integracao: evento A migrado vs evento B legado

## objetivo

Cumprir os criterios Given/When/Then da US: no ambiente de integracao (pytest +
SQLite de teste ou Postgres de CI, conforme padrao do repo), dois eventos A e B
coexistem; apenas A esta no novo fluxo; operacoes relevantes demonstram B no
**agregado legado** e A no caminho **migrado** (ou no hook preparado em T3),
com **asserts ou logs verificaveis** na execucao da suite.

## precondicoes

- T3 `done`: routers invocam o servico de gate.
- Fixtures de `Evento` (ou equivalente) reutilizaveis nos testes do backend.

## orquestracao

- `depends_on`: T3.
- `parallel_safe`: `false`.
- `write_scope`: novos ou estendidos ficheiros sob `backend/tests/`.

## arquivos_a_ler_ou_tocar

- `backend/tests/conftest.py` *(fixtures existentes)*
- `backend/tests/test_ativos_endpoints.py` ou equivalente
- `backend/tests/test_ingressos_endpoints.py` ou equivalente
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/user-stories/US-2-03-ROLLOUT-POR-EVENTO/README.md`

## testes_red

- testes_a_escrever_primeiro:
  - Cenario integrado: setup evento A (novo fluxo) e B (legado); chamar
    endpoint(s) escolhido(s) em T3 e assertar diferenca de comportamento ou
    presenca de log/campo que prove qual modo foi aplicado *(alinhado ao que
    T3 implementou)*.
- comando_para_rodar:
  - `cd backend && PYTHONPATH=..:. SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q -k rollout`
  *(ajustar `-k` ao nome dos testes criados)*
- criterio_red:
  - Se T3 estiver incompleto, estes testes falham de forma clara; apos T3
    completo, devem passar (green).

## passos_atomicos

1. Escrever fixtures minimas para A/B e estado de gate conforme T1.
2. Escrever testes red cobrindo pelo menos um endpoint em ativos e um em
   ingressos *(ou justificar um unico arquivo se o PRD baseline agrupar)*.
3. Executar suite ate green; capturar evidencia (trecho de log ou assert) para
   auditoria.
4. Documentar no docstring do teste o mapeamento para o Given/When/Then da US.

## comandos_permitidos

- `cd backend && PYTHONPATH=..:. SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q`
- `cd backend && PYTHONPATH=..:. SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q --tb=long` *(debug)*

## resultado_esperado

Suite de integracao exercita o gate com resultado verificavel; rastreio claro
ate aos criterios de aceite da US-2-03.

## testes_ou_validacoes_obrigatorias

- Nenhum teste flaky: usar transacoes/fixtures isoladas conforme padrao do
  repo.
- `pytest` completo da pasta nova/alterada sem falhas.

## stop_conditions

- Parar se o ambiente de teste nao suportar dois eventos sem refator de
  fixtures — documentar lacuna e reduzir escopo com PM.
- Parar se nao houver endpoint observavel diferenciando modos apos T3.
