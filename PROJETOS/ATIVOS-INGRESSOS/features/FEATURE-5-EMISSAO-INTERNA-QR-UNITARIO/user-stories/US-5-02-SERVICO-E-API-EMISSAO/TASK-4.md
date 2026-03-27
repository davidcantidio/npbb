---
doc_id: "TASK-4.md"
user_story_id: "US-5-02-SERVICO-E-API-EMISSAO"
task_id: "T4"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T3"
parallel_safe: false
write_scope:
  - "backend/app/routers/ingressos.py"
  - "backend/app/schemas/ingressos.py"
  - "backend/app/services/"
  - "backend/tests/test_ingressos_endpoints.py"
  - "backend/tests/test_emissao_interna_unitario_service.py"
tdd_aplicavel: true
---

# TASK-4 - Idempotencia documentada e sem duplicata indevida

## objetivo

Definir e implementar **escopo de idempotencia** (ex.: header `Idempotency-Key`, hash canonicos do corpo, ou campo explicito no JSON) para emissao individual e lote (se aplicavel), de forma que **requisicoes equivalentes** nao criem segunda emissao indevida. Documentar o comportamento na OpenAPI (descricao do parametro/header e semantica 200 vs 201 se o projeto adotar resposta repetivel).

## precondicoes

- TASK-3 (`T3`) `done`.
- [US-5-01](../US-5-01-MODELO-E-MIGRACAO-EMISSAO-UNITARIA/README.md) `done`.

## orquestracao

- `depends_on`: `T3`.
- `parallel_safe`: `false`.
- `write_scope`: tocar servico e router conforme onde a chave for interpretada (preferencia: validacao na borda HTTP + persistencia ou cache no servico).

## arquivos_a_ler_ou_tocar

- `backend/app/routers/ingressos.py`
- `backend/app/schemas/ingressos.py`
- Modulo de servico de emissao criado na TASK-1
- `backend/tests/test_ingressos_endpoints.py`
- `backend/tests/test_emissao_interna_unitario_service.py` *(se logica compartilhada)*

## testes_red

- testes_a_escrever_primeiro:
  - Teste de API: duas chamadas **equivalentes** (mesmo escopo de idempotencia) resultam em **uma** emissao persistida e segunda resposta coerente (mesmo id publico ou 200 com mesmo recurso — documentar escolha na task antes de green).
  - Teste: requisicao equivalente com **corpo distinto** em campo fora do escopo de idempotencia se comporta conforme documentacao (aceitar, rejeitar ou `409` — alinhar ao PRD; se silencioso na US, preferir `409` ou erro de negocio explicito).
- comando_para_rodar:
  - `cd backend && PYTHONPATH="${PWD}/..:${PWD}" SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_ingressos_endpoints.py tests/test_emissao_interna_unitario_service.py -q`
- criterio_red:
  - Testes de idempotencia falham ate implementacao existir.

## passos_atomicos

1. Escrever os testes listados em `testes_red`.
2. Rodar pytest e confirmar red.
3. Especificar no codigo e na OpenAPI o **escopo exato** da chave (quais campos entram no fingerprint).
4. Implementar deduplicacao (tabela dedicada, coluna unica, ou lookup por chave conforme modelo US-5-01 permitir).
5. Rodar pytest, green; atualizar descricao OpenAPI para desenvolvedores integradores.

## comandos_permitidos

- `cd backend && PYTHONPATH="${PWD}/..:${PWD}" SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_ingressos_endpoints.py tests/test_emissao_interna_unitario_service.py -q`
- `cd backend && ruff check app/routers/ingressos.py app/schemas/ingressos.py app/services/`

## resultado_esperado

- Comportamento idempotente verificavel e **documentado na API**.
- Criterio **Given** repeticao equivalente / **Then** sem duplicata indevida atendido.

## testes_ou_validacoes_obrigatorias

- Testes de idempotencia verdes.
- Leitura humana do trecho OpenAPI gerado para o header/campo de idempotencia.

## stop_conditions

- Parar se o modelo US-5-01 nao permitir armazenar chave de idempotencia sem nova migration — nesse caso registrar `BLOQUEADO` e encaminhar extensao a US-5-01 ou nova US de persistencia.
