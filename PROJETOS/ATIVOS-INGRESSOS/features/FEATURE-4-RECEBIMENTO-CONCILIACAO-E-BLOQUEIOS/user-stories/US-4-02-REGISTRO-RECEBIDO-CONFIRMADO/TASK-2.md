---
doc_id: "TASK-2.md"
user_story_id: "US-4-02-REGISTRO-RECEBIDO-CONFIRMADO"
task_id: "T2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "backend/app/schemas/recebimento_confirmado.py"
  - "backend/app/routers/recebimentos_ativos.py"
  - "backend/app/main.py"
tdd_aplicavel: false
---

# TASK-2 - API REST: submissao de lote e consulta de historico

## objetivo

Expor endpoints FastAPI para (1) submeter lote de recebimento com os eixos e
payload alinhados ao servico da TASK-1 e (2) consultar registos de
recebimento/historico minimo no mesmo contexto (evento, diretoria, categoria,
modo externo), cumprindo os criterios "consultavel" e "historico de
recebimentos" da US-4-02. Contrato JSON pensado para evolucao FEATURE-7
(integracao) sem antecipar autenticacao de sistema externo completa.

## precondicoes

- TASK-1 `done`: servico de dominio importavel e estavel.
- Padrao de autenticacao existente (`get_current_user` ou equivalente) revisado
  para aplicar RBAC coerente com operador interno.
- Prefixo e naming de rotas alinhados a convencao do projeto (evitar colisao
  com `backend/app/routers/ativos.py`).

## orquestracao

- `depends_on`: `["T1"]`.
- `parallel_safe`: `false`.
- `write_scope`: schemas dedicados, router dedicado, registo em `main.py`.

## arquivos_a_ler_ou_tocar

- `backend/app/routers/ativos.py` *(convencoes de listagem e erros HTTP)*
- `backend/app/core/auth.py`
- `backend/app/utils/http_errors.py`
- `backend/app/main.py`
- `backend/app/schemas/recebimento_confirmado.py` *(criar)*
- `backend/app/routers/recebimentos_ativos.py` *(criar; nome ajustavel se gate
  fixar outro modulo)*
- `backend/app/services/recebimento_confirmado_service.py`

## testes_red

> Nao aplicavel (`tdd_aplicavel: false`).

## passos_atomicos

1. Definir schemas Pydantic de entrada (lote, linhas ou agregado conforme
   servico), validacoes de tipo/tamanho e campos opcionais de artefato.
2. Definir schemas de saida para linha de recebimento e para listagem de
   historico (incluir instante e identificador de ator conforme trilha).
3. Criar router com prefixo estavel (ex.: `/ativos/recebimentos` ou
   `/recebimentos/confirmados`) e POST para criacao em lote chamando o servico
   T1 dentro de `Depends(get_session)` e utilizador corrente.
4. Implementar GET (ou GET paginado) filtrando por evento, diretoria, categoria
   e modo externo, retornando lista ordenada por tempo descendente ou ordem
   acordada no modelo.
5. Registar o router em `backend/app/main.py` com mesma ordem de tags que
   facilita documentacao OpenAPI.
6. Mapear erros de dominio para HTTP 4xx/5xx com `raise_http_error` ou padrao
   existente.

## comandos_permitidos

- `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend python -c "from app.main import app"` *(import smoke)*
- `cd backend && ruff check app/routers/recebimentos_ativos.py app/schemas/recebimento_confirmado.py`

## resultado_esperado

API documentada no OpenAPI com POST de lote e GET de historico/consulta,
autenticada como as demais rotas operacionais, sem logica de negocio duplicada
fora do servico T1.

## testes_ou_validacoes_obrigatorias

- Chamada manual via `/docs` ou cliente HTTP: POST seguido de GET com os mesmos
  filtros devolve o registo criado *(validacao integral automatizada na TASK-3)*.

## stop_conditions

- Parar se o servico T1 exigir alteracao de assinatura que quebre escopo —
  retornar T1 a `active` com nota, nao alargar escopo da US-4-02.
- Parar se nao houver criterio de autorizacao claro (operador vs agencia);
  escalar para alinhamento RBAC antes de expor endpoint.
