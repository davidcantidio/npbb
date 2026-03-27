---
doc_id: "TASK-2.md"
user_story_id: "US-6-01-DISTRIBUICAO-RESPEITANDO-SALDO-DISPONIVEL"
task_id: "T2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "backend/app/routers/ingressos.py"
  - "backend/app/schemas/ingressos.py"
  - "backend/app/services/"
tdd_aplicavel: true
---

# TASK-2 - Dominio e API: validar disponivel, transacao e resposta HTTP

## objetivo

Implementar o caso de uso de **confirmacao de distribuicao** para origem
externa: calcular ou ler o `disponivel` (FEATURE-4), **rejeitar** quando a
quantidade solicitada exceder o saldo (AC1 — mensagem clara, sem alteracao
persistida inconsistente); em caso de sucesso persistir distribuicao com estado
`distribuido` e trilha auditavel (AC2); garantir que transacoes nao violam
invariantes de emissao interna / FEATURE-5 (AC3).

## precondicoes

- [TASK-1](./TASK-1.md) `done`: migracoes aplicadas e modelos de distribuicao
  disponiveis.
- Contrato de autenticacao e autorizacao existente em
  `backend/app/routers/ingressos.py` compreendido *(perfis operador / admin)*.

## orquestracao

- `depends_on`: `["T1"]`.
- `parallel_safe`: `false`.
- `write_scope`: router e schemas de ingressos; novo ou existente modulo sob
  `backend/app/services/` *(ex.: `distribuicao_ingressos_service.py` — nome
  final na execucao)*.

## arquivos_a_ler_ou_tocar

- [README.md](./README.md)
- [TASK-1](./TASK-1.md)
- `backend/app/routers/ingressos.py`
- `backend/app/schemas/ingressos.py`
- Servicos e modelos FEATURE-4 / FEATURE-5 tocados por `disponivel` e emissao
  interna
- `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md` sec. 2.3–2.4

## testes_red

- testes_a_escrever_primeiro:
  - Teste API (pytest): dado saldo `disponivel` insuficiente, `POST` (ou verbo
    acordado) de confirmacao de distribuicao retorna erro 4xx com `code` stable
    e `message` legivel; nenhuma linha nova de distribuicao persistida.
  - Teste API: dado saldo suficiente, confirmacao persiste distribuicao com
    estado `distribuido` e campos de trilha preenchidos.
- comando_para_rodar:
  - `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ingressos_endpoints.py -k "<padrao_distribuicao>"`
- criterio_red:
  - Os testes novos falham antes da implementacao; se passarem, revisar
    cobertura ou duplicacao.

## passos_atomicos

1. Escrever os testes listados em `testes_red` e confirmar falha inicial.
2. Implementar servico de dominio: obter `disponivel` para o eixo
   evento/categoria/origem externa; validar quantidade; executar escrita em
   transacao unica (rollback total em violacao).
3. Acoplar emissao interna (FEATURE-5) quando o fluxo exigir — apenas leitura
   ou escrita ja definida no modelo; nao alargar escopo a novos tipos de
   emissao.
4. Expor endpoint(s) em `ingressos.py` com schemas Pydantic de request/response;
   mapear erros de dominio para HTTP com corpo alinhado ao padrao do router
   (`raise_http_error` ou equivalente).
5. Rodar testes ate green; refatorar mantendo transacao e mensagens estaveis.

## comandos_permitidos

- `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ingressos_endpoints.py`
- `cd backend && ruff check app/routers/ingressos.py app/schemas/ingressos.py app/services/`

## resultado_esperado

API utilizavel pela UI que implementa AC1–AC3 na camada backend, com testes
novos passando.

## testes_ou_validacoes_obrigatorias

- Pytest: cenarios `testes_red` em green.
- Verificacao manual opcional: Swagger/OpenAPI se existir para o router.

## stop_conditions

- Parar se a definicao de `disponivel` no codigo divergir do PRD sem ADR —
  escalar a PM/FEATURE-4.
- Parar se FEATURE-5 nao tiver hook claro e AC3 ficar ambigua; nao improvisar
   regra de emissao fora da US.
