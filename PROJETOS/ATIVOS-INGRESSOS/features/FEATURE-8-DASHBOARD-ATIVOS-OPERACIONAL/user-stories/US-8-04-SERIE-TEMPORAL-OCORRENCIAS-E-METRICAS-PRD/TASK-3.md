---
doc_id: "TASK-3.md"
user_story_id: "US-8-04-SERIE-TEMPORAL-OCORRENCIAS-E-METRICAS-PRD"
task_id: "T3"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "backend/app/"
  - "backend/tests/"
tdd_aplicavel: true
---

# T3 - API read-only: resumo de problemas / ocorrencias por evento (minimo v1)

## objetivo

Expor endpoint read-only que suporta o **painel minimo v1** de ocorrencias/problemas: para um `evento_id`, retornar **contagem total** e **lista resumida** (ex.: ultimos N registos ordenados por data, com tipo + descricao truncada + `registrado_em`), sem implementar drill-down profundo do [Intake sec. 14](../../../../INTAKE-ATIVOS-INGRESSOS.md). Reutilizar o modelo de dominio de problemas entregue pela FEATURE-6 / USs de problemas quando ja existir no codigo; caso contrario, consumir a mesma fonte de verdade que a dimensao **problemas** da US-8-01.

## precondicoes

- **T1** `done` *(partilha convencao de router RBAC e agrupamento por evento com o dashboard ativos)*.
- Dados de problema operacional disponiveis via dominio existente (tabelas/servicos da FEATURE-6).

## orquestracao

- `depends_on`: `["T1"]`.
- `parallel_safe`: false.
- `write_scope`: `backend/app/` (router/servico/schema do resumo de problemas), `backend/tests/`.

## arquivos_a_ler_ou_tocar

- [README.md](README.md) desta US
- [TASK-1.md](TASK-1.md)
- [US-6-04](../../../FEATURE-6-DISTRIBUICAO-REMANEJAMENTO-AJUSTES-PROBLEMAS/user-stories/US-6-04-PROBLEMAS-OPERACIONAIS/README.md) e codigo associado em `backend/app/`
- [PRD-ATIVOS-INGRESSOS.md](../../../../PRD-ATIVOS-INGRESSOS.md) — estado `problema_registrado`, sec. 2.4
- `backend/tests/` — fixtures de evento e problema se existirem

## testes_red

- **testes_a_escrever_primeiro**:
  - Teste de API: GET com `evento_id` com problemas seedados retorna `total` > 0 e lista com campos minimos.
  - Teste: evento sem problemas retorna `total: 0` e lista vazia, status 200.
- **comando_para_rodar**:
  - `cd backend && PYTHONPATH=$(pwd)/..:$(pwd) SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/<path_do_teste>`
- **criterio_red**:
  - Falha antes da implementacao; se passar, rever se o endpoint ja existia.

## passos_atomicos

1. Escrever testes de `testes_red`.
2. Confirmar red.
3. Implementar servico de leitura: query filtrada por `evento_id`, limite N (ex.: 20) configuravel com teto maximo no backend para evitar abuso.
4. Expor schema Pydantic/OpenAPI claro (`total`, `items[]`).
5. Integrar router sob o mesmo prefixo de dashboard ativos ou modulo API acordado com T1.
6. Green + refatoracao minima.

## comandos_permitidos

- `cd backend && PYTHONPATH=... TESTING=true python -m pytest -q`
- `ruff check` nos ficheiros tocados

## resultado_esperado

Contrato estavel para alimentar o painel v1 da **T4**, alinhado ao segundo criterio Given/When/Then da US-8-04.

## testes_ou_validacoes_obrigatorias

- Pytest verde para os cenarios seed / vazio.
- Documentacao OpenAPI ou interna do limite N e campos.

## stop_conditions

- Parar se nao existir persistencia de problemas no ambiente — completar entregas de dominio necessarias ou alinhar com PM para mock apenas em dev (nao em producao).
