---
doc_id: "TASK-3.md"
user_story_id: "US-5-02-SERVICO-E-API-EMISSAO"
task_id: "T3"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "backend/app/routers/ingressos.py"
  - "backend/app/platform/security/rbac.py"
  - "backend/tests/test_ingressos_endpoints.py"
tdd_aplicavel: true
---

# TASK-3 - RBAC e negacao sem vazamento na emissao

## objetivo

Garantir que apenas **operador ou integracao autorizada** (conforme modelo de permissoes do projeto) acione as rotas de emissao; em caso de negacao, retornar **403/401** com mensagens genericas e **sem** expor dados sensiveis do destinatario, QR ou internals no corpo da resposta. Alinhar a dependencias FastAPI existentes (`get_current_user`, `require_internal_user` / extensoes em `rbac.py` se necessario).

## precondicoes

- TASK-2 (`T2`) `done` (rotas de emissao existentes).
- [US-5-01](../US-5-01-MODELO-E-MIGRACAO-EMISSAO-UNITARIA/README.md) `done`.

## orquestracao

- `depends_on`: `T2`.
- `parallel_safe`: `false`.
- `write_scope`: conforme frontmatter.

## arquivos_a_ler_ou_tocar

- `backend/app/platform/security/rbac.py`
- `backend/app/core/auth.py`
- `backend/app/models/models.py` *(Usuario, UsuarioTipo, permissoes)*
- `backend/app/routers/ingressos.py`
- `backend/tests/test_ingressos_endpoints.py`
- Outros routers que apliquem padrao semelhante de autorizacao *(referencia)*

## testes_red

- testes_a_escrever_primeiro:
  - Teste: usuario **sem** permissao (ou nao autenticado) chama POST de emissao e recebe **403** ou **401** conforme padrao do projeto; corpo **nao** contem email completo, token QR, ou PII de terceiros em campos de detalhe.
  - Teste: usuario **com** permissao adequada continua a obter sucesso no cenario feliz (regressao TASK-2).
- comando_para_rodar:
  - `cd backend && PYTHONPATH="${PWD}/..:${PWD}" SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_ingressos_endpoints.py -q`
- criterio_red:
  - Os testes de negacao devem falhar ate as dependencias de autorizacao estarem aplicadas nas rotas de emissao.

## passos_atomicos

1. Escrever os testes listados em `testes_red`.
2. Rodar pytest e confirmar red.
3. Aplicar `Depends` com politica de papel/escopo acordada (reutilizar `require_npbb_user` ou criar dependencia especifica para emissao se o PRD distinguir operador vs integracao).
4. Revisar mensagens e payloads de erro para nao incluir dados sensiveis (criterio LGPD da US).
5. Rodar pytest, green; refatorar se necessario.

## comandos_permitidos

- `cd backend && PYTHONPATH="${PWD}/..:${PWD}" SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_ingressos_endpoints.py -q`
- `cd backend && ruff check app/routers/ingressos.py app/platform/security/rbac.py`

## resultado_esperado

- Todas as rotas de emissao protegidas de forma consistente com o restante do backend.
- Criterio **Given** usuario sem permissao / **Then** negacao sem vazamento atendido e coberto por testes.

## testes_ou_validacoes_obrigatorias

- Testes de autorizacao negativa e regressao do happy path verdes.
- Revisao manual de uma resposta 403 JSON (sem PII).

## stop_conditions

- Parar e reportar `BLOQUEADO` se o projeto nao tiver criterio objetivo de quem pode emitir (papeis); exigir decisao no README da US ou manifesto antes de inventar papeis novos.
