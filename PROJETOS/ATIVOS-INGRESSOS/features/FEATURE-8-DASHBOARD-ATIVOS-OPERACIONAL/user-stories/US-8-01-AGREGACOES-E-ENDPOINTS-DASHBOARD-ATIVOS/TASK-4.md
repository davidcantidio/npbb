---
doc_id: "TASK-4.md"
user_story_id: "US-8-01-AGREGACOES-E-ENDPOINTS-DASHBOARD-ATIVOS"
task_id: "T4"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T3"
parallel_safe: false
write_scope:
  - "backend/app/routers/dashboard_ativos.py"
  - "backend/app/main.py"
tdd_aplicavel: false
---

# T4 - Router FastAPI e registro no app

## objetivo

Expor **endpoint(s) GET read-only** para o dashboard de ativos sob prefixo alinhado ao modulo existente de leads (`/dashboard` — ver [`dashboard_leads.py`](../../../../../../backend/app/routers/dashboard_leads.py)): por exemplo `/dashboard/ativos` ou subcaminho acordado. Usar `get_current_user`, aplicar **mesmo padrao de visibilidade** (agencia / evento) que outros dashboards ou listagens de ativos no repo. Parametros de query devem refletir o schema T1 (`evento_id`, filtros opcionais incl. diretoria se o contrato T1 previr). Resposta: modelo Pydantic T1 com codigo HTTP 200 em caso feliz; **4xx** para recurso fora de escopo ou evento invalido, alinhado a `raise_http_error` ou equivalente.

## precondicoes

- [T3](TASK-3.md) concluida: servico de agregacao funcional.
- [T1](TASK-1.md) concluida: query/response estaveis.
- Padrao de autenticacao e erros HTTP do projeto revisado.

## orquestracao

- `depends_on`: `T3`.
- `parallel_safe`: `false`.
- `write_scope`: novo router e `include_router` em `main.py`.

## arquivos_a_ler_ou_tocar

- `backend/app/routers/dashboard_leads.py`
- `backend/app/core/auth.py` ou modulo de `get_current_user`
- `backend/app/utils/http_errors.py`
- `backend/app/main.py`
- `backend/app/services/dashboard_ativos.py`
- **Criar**: `backend/app/routers/dashboard_ativos.py`

## passos_atomicos

1. Criar `APIRouter` com `prefix` e `tags` coerentes com OpenAPI (ex. `tags=["dashboard"]`).
2. Implementar handler GET que parseia query params para o modelo T1, invoca servico T3 e retorna response model.
3. Aplicar filtros de visibilidade ao `evento_id` / diretoria conforme usuario atual (espelhar logica de `dashboard_leads` ou `ativos.py` — documentar qual padrao foi seguido).
4. Registrar router em `backend/app/main.py` com `app.include_router(...)`.
5. Verificar documentacao OpenAPI em `/docs` (campos das oito dimensoes visiveis no schema).

## comandos_permitidos

- `cd backend && PYTHONPATH=$(pwd)/..:$(pwd) SECRET_KEY=ci-secret-key TESTING=true .venv/bin/uvicorn app.main:app --reload` *(smoke local, opcional)*
- `cd backend && .venv/bin/ruff check app/routers/dashboard_ativos.py app/main.py`

## resultado_esperado

- Endpoint documentado consumivel pelo frontend (US-8-03/8-04 dependem deste contrato).
- RBAC e erros alinhados ao restante da API.

## testes_ou_validacoes_obrigatorias

- Smoke manual ou preparacao para T5: GET com token valido e `evento_id` elegivel retorna 200 e JSON que valida contra schema.

## stop_conditions

- Parar se o contrato T1 nao incluir parametro necessario a visibilidade (ex. diretoria) mas o PRD exigir filtro — voltar a T1 com ajuste documental antes de codar.
- Parar se for necessario expor POST ou mutacao — fora do escopo read-only desta US.
