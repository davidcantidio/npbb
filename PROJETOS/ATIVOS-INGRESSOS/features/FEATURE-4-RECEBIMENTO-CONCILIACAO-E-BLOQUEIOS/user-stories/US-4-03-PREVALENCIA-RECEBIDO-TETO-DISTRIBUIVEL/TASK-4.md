---
doc_id: "TASK-4.md"
user_story_id: "US-4-03-PREVALENCIA-RECEBIDO-TETO-DISTRIBUIVEL"
task_id: "T4"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T2"
  - "T3"
parallel_safe: false
write_scope:
  - "backend/tests/test_ativos_ingressos_us4_03_integration.py"
tdd_aplicavel: false
---

# TASK-4 - Testes de integracao dos tres criterios Given/When/Then

## objetivo

Fechar a US com uma suite de integracao (HTTP ou servico + DB de teste) que demonstre, de ponta a ponta, os **tres** criterios de aceitacao do [README.md](./README.md): teto pelo recebido; consulta auditavel de divergencia; distribuicao limitada a zero sem recebido confirmado.

## precondicoes

- T2 e T3 `done`.
- Fixtures ou factories disponiveis para criar evento, cota/lote externo, recebimento e solicitacao conforme modelo da FEATURE-4.

## orquestracao

- `depends_on`: `T2`, `T3`.
- `parallel_safe`: `false`.
- `write_scope`: conforme frontmatter *(ficheiro de teste dedicado para nao inflar suites lentas existentes sem necessidade)*.

## arquivos_a_ler_ou_tocar

- `backend/tests/test_ativos_ingressos_us4_03_integration.py` *(criar)*
- `backend/tests/test_ingressos_endpoints.py`
- `backend/tests/test_ativos_endpoints.py`
- `backend/tests/conftest.py` *(apenas se precisar de fixtures partilhadas minimas)*

## passos_atomicos

1. Criar modulo de teste com cenario **planejado > recebido**: listagem ou solicitacao respeita teto igual ao recebido.
2. Adicionar cenario **recebido > planejado**: teto e delta refletem prevalencia do recebido na API de T3 e na distribuicao.
3. Adicionar cenario **sem recebido confirmado**: disponivel para distribuicao externa zero e POST de solicitacao falha ou retorna conflito conforme implementacao T2.
4. Opcional: um teste que chama o endpoint de divergencia T3 e valida os tres campos no mesmo fixture.
5. Garantir que os comandos de CI documentados em AGENTS.md executam esta suite.

## comandos_permitidos

- `cd backend && PYTHONPATH=..:. SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ativos_ingressos_us4_03_integration.py`

## resultado_esperado

- Ficheiro de integracao green em ambiente `TESTING=true` (SQLite de teste).
- Rastreabilidade clara nos nomes de teste para os Given/When/Then da US.

## testes_ou_validacoes_obrigatorias

- `pytest -q tests/test_ativos_ingressos_us4_03_integration.py` em green apos T2/T3.
- Revisar se nenhum teste depende de ordem fragil ou estado partilhado nao isolado.

## stop_conditions

- Parar com `BLOQUEADO` se fixtures de FEATURE-4 ainda nao permitirem persistir recebido/planejado no ambiente de teste.
- Parar se a duplicacao com testes de T2/T3 for total: nesse caso cancelar T4 com justificativa e mover assercoes para as tasks anteriores *(requer atualizacao documental da US)*.
