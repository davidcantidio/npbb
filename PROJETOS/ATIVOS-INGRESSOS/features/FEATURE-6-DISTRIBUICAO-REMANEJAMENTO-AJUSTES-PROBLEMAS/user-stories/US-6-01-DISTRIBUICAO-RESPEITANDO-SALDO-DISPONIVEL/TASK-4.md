---
doc_id: "TASK-4.md"
user_story_id: "US-6-01-DISTRIBUICAO-RESPEITANDO-SALDO-DISPONIVEL"
task_id: "T4"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "backend/tests/test_ingressos_endpoints.py"
tdd_aplicavel: false
---

# TASK-4 - Testes de integracao e evidencia dos criterios Given/When/Then

## objetivo

Consolidar **evidencia automatizada** para a US-6-01: garantir que a suite
(ou subconjunto dedicado) em `test_ingressos_endpoints.py` documente
explicitamente os tres Given/When/Then do README — incluindo persistencia e
trilha apos sucesso e ausencia de violacao de invariantes FEATURE-5 nas
transacoes verificadas *(pode estender testes iniciados na TASK-2 se ainda
faltarem assercoes de trilha ou de emissao interna)*.

## precondicoes

- [TASK-2](./TASK-2.md) `done`.
- [TASK-3](./TASK-3.md) `done` ou em paralelo documental: esta task foca
  **backend**; nao exige E2E de browser.

## orquestracao

- `depends_on`: `["T2"]` *(T3 nao e predecessora tecnica dos testes de API)*.
- `parallel_safe`: `false`.
- `write_scope`: apenas `backend/tests/test_ingressos_endpoints.py` salvo
  fixtures partilhadas ja existentes no modulo de testes.

## arquivos_a_ler_ou_tocar

- [README.md](./README.md) — criterios de aceitacao
- [TASK-2](./TASK-2.md)
- `backend/tests/test_ingressos_endpoints.py`
- Factories ou fixtures de evento/cota/recebimento existentes no backend

## testes_red

> Nao aplicavel (`tdd_aplicavel: false`); reforco de cobertura apos implementacao.

## passos_atomicos

1. Revisar testes introduzidos na TASK-2; renomear ou comentar com referencia
   explicita ao criterio AC1/AC2/AC3 quando util para revisao.
2. Adicionar assercoes faltantes: consulta pos-POST confirma trilha (ator,
   timestamp, destinatario); estado `distribuido`; para AC3, assert sobre
   ligacao ou contagem de emissao interna conforme modelo FEATURE-5.
3. Cobrir caso limite: saldo exato igual a quantidade solicitada (deve passar).
4. Garantir isolamento com `TESTING=true` / transacoes de teste conforme
  `AGENTS.md`.
5. Documentar no docstring do teste ou comentario curto o mapeamento
   Given/When/Then para auditoria futura.

## comandos_permitidos

- `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ingressos_endpoints.py`

## resultado_esperado

Suite pytest verde com evidencia legivel dos tres criterios da US no ficheiro
canonico de testes de ingressos.

## testes_ou_validacoes_obrigatorias

- Comando pytest acima sem falhas.
- Nenhum teste flaky introduzido *(repetir uma vez se houver ordem dependente)*.

## stop_conditions

- Parar se fixtures nao permitirem simular `disponivel` de origem externa —
  completar dados de seed ou helpers na TASK-2 antes de prosseguir.
- Parar se AC3 nao for assertavel sem mocks frageis — registrar lacuna objetiva
  no README da US sob limitacoes de handoff.
