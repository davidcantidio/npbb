---
doc_id: "TASK-3.md"
user_story_id: "US-7-03-ENDPOINTS-INGESTAO-E-FLUXO-OPERACIONAL"
task_id: "T3"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "backend/app/routers/ingestao_externa.py"
  - "backend/app/services/ingestao_externa_idempotencia.py"
  - "backend/tests/test_ingestao_externa_idempotencia.py"
tdd_aplicavel: true
---

# TASK-3 - Integracao de idempotencia na ingestao externa

## objetivo

Garantir que reenvios da mesma operacao com a **mesma chave de idempotencia**
(conforme [US-7-01](../US-7-01-MODELO-IDEMPOTENCIA-E-CHAVES-EXTERNAS/README.md))
nao duplicam efeitos colaterais de negocio e devolvem resposta coerente com a
primeira resposta bem-sucedida (ou erro repetido, conforme politica definida na
US-7-01).

## precondicoes

- [US-7-01](../US-7-01-MODELO-IDEMPOTENCIA-E-CHAVES-EXTERNAS/README.md) concluida
  (`done`): tabelas/servicos de idempotencia e chaves externas disponiveis.
- [TASK-2](./TASK-2.md) concluida: endpoint e payloads validaveis.
- Localizar no codigo os repositorios ou servicos expostos pela US-7-01
  *(caminhos exatos apos merge)*.

## orquestracao

- `depends_on`: `T2`.
- `parallel_safe`: `false`.
- `write_scope`: camadas HTTP + servico auxiliar de idempotencia e testes;
  nao alterar esquema de BD da US-7-01 sem gate.

## arquivos_a_ler_ou_tocar

- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-7-CONTRATOS-API-AUTOMACAO-EXTERNA/user-stories/US-7-01-MODELO-IDEMPOTENCIA-E-CHAVES-EXTERNAS/README.md`
- Artefactos de persistencia e servicos da US-7-01 *(paths concretos na execucao)*
- `backend/app/routers/ingestao_externa.py`
- `backend/app/services/ingestao_externa_idempotencia.py` *(criar ou ajustar nome
  a convencao do modulo)*
- `backend/tests/test_ingestao_externa_idempotencia.py` *(criar)*

## testes_red

- testes_a_escrever_primeiro:
  - primeiro POST com chave A e payload valido persiste/regista idempotencia e
    retorna corpo C1.
  - segundo POST com mesma chave A e mesmo payload retorna C1 (ou equivalente
    documentado) sem segundo efeito de escrita de negocio.
  - POST com mesma chave A e payload divergente retorna 409 (ou codigo acordado
    na US-7-01).
- comando_para_rodar:
  - `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ingestao_externa_idempotencia.py`
- criterio_red:
  - testes devem falhar ate a integracao estar implementada; se passarem antes,
    parar e rever duplicacao de logica ou mocks incorretos.

## passos_atomicos

1. Escrever os testes listados em `testes_red` usando base de dados de teste
   (`TESTING=true`).
2. Rodar e confirmar red.
3. Implementar orquestracao: antes da logica de negocio (T4), consultar/registar
   chave no store da US-7-01; em reenvio, short-circuit com resposta armazenada.
4. Propagar `correlation_id` se existir, sem conflitar com a chave de
   idempotencia *(semantica na US-7-01)*.
5. Green + refatoracao local mantendo invariantes.

## comandos_permitidos

- `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ingestao_externa_idempotencia.py`
- `cd backend && ruff check app/routers/ingestao_externa.py app/services/ingestao_externa_idempotencia.py`

## resultado_esperado

Endpoint de ingestao externa respeita deduplicacao por chave alinhada a US-7-01
e criterios Given/When/Then da US-7-03 sobre reenvio.

## testes_ou_validacoes_obrigatorias

- `pytest` do modulo de idempotencia em green.
- Verificacao manual opcional: duas chamadas curl com mesmo header/campo de
  chave.

## stop_conditions

- Parar se US-7-01 nao entregar API de persistencia utilizavel — `BLOQUEADO`
  ate concluir US-7-01.
- Parar se a politica de conflito payload+chave nao estiver definida; pedir
  decisao ao manifesto FEATURE-7 / US-7-01 sem improvisar semantica.
