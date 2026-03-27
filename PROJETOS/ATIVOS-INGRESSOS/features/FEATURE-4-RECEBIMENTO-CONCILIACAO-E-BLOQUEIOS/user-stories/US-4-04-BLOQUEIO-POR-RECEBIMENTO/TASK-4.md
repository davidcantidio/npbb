---
doc_id: "TASK-4.md"
user_story_id: "US-4-04-BLOQUEIO-POR-RECEBIMENTO"
task_id: "T4"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T3"
parallel_safe: false
write_scope:
  - "backend/tests/test_ativos_bloqueio_recebimento.py"
  - "PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS/user-stories/US-4-04-BLOQUEIO-POR-RECEBIMENTO/README.md"
tdd_aplicavel: false
---

# TASK-4 - Testes de dominio e evidencia no README da US

## objetivo

Cobrir os tres criterios Given/When/Then da [US-4-04](./README.md) com testes automatizados de dominio (preferencialmente sem acoplar a UI), e registrar no README da US referencias breves a ficheiros de teste e comandos de validacao, cumprindo o artefato minimo da US.

## precondicoes

- TASK-3 `done`: bloqueio e desbloqueio implementados e integrados.
- Suite de testes do backend com `TESTING=true` e SQLite funcional conforme [AGENTS.md](../../../../../../AGENTS.md).

## orquestracao

- `depends_on`: `T3`.
- `parallel_safe`: `false`.
- `write_scope`: o ficheiro de teste pode ser partido em mais modulos se o projeto exigir; manter um entrypoint claro citado no README.

## arquivos_a_ler_ou_tocar

- `backend/tests/test_ativos_bloqueio_recebimento.py` *(criar)*
- `backend/tests/conftest.py` *(fixtures existentes de client/engine)*
- `backend/tests/test_ativos_endpoints.py` *(padroes de autenticacao e dados minimos)*
- [README.md](./README.md) *(secao artefato / evidencia — apenas linhas necessarias, sem alterar criterios da US)*

## passos_atomicos

1. Escrever testes para: (a) aumento dependente de ticketeira sem cobertura → permanece bloqueado com motivo esperado; (b) apos simular recebimento + conciliacao com cobertura → bloqueio levantado e saldo/teto respeitado; (c) aumento nao dependente de ticketeira → nao recebe `bloqueado_por_recebimento` por esta regra.
2. Usar factories/fixtures alinhadas ao que US-4-01/4-02/4-03 ja criaram; se dados minimos ainda nao existirem, criar setup local no ficheiro de teste documentado como temporario ate estabilizacao do seed.
3. Rodar a suite focada e corrigir flakiness (transacoes, isolamento).
4. Atualizar o README da US com subsecao curta “Evidencias de teste” (comandos + paths) sem duplicar o DoD inteiro.

## comandos_permitidos

- `cd backend && PYTHONPATH=<raiz>:<raiz>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_ativos_bloqueio_recebimento.py -q`
- `cd backend && PYTHONPATH=<raiz>:<raiz>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_ativos_endpoints.py -q` *(regressao rapida se T2 tocou router)*

## resultado_esperado

- Testes verdes que demonstram os tres criterios da US.
- README da US aponta para evidencia executavel.

## testes_ou_validacoes_obrigatorias

- Comando pytest do ficheiro novo passa localmente em CI-paridade (`TESTING=true`).

## stop_conditions

- Parar e reportar `BLOQUEADO` se nao for possivel construir dados de teste sem US-4-01/4-02/4-03 mergeadas — listar dependencia objetiva.
- Parar se T3 nao estiver `done`.
