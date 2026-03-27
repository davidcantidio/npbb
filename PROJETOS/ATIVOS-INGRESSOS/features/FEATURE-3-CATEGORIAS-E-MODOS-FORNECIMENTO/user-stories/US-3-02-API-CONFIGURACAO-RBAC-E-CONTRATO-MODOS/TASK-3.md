---
doc_id: "TASK-3.md"
user_story_id: "US-3-02-API-CONFIGURACAO-RBAC-E-CONTRATO-MODOS"
task_id: "T3"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "backend/app/routers/ativos.py"
  - "backend/app/core/auth.py"
tdd_aplicavel: false
---

# TASK-3 - RBAC na escrita de configuracao por evento (403 sem efeitos colaterais)

## objetivo

Garantir que apenas perfis autorizados alterem a configuracao de categorias por evento (alinhado a PRD 2.6 / restricoes LGPD-operacao citadas na US), negando com **HTTP 403** e corpo de erro explicito quando o cliente nao tiver permissao, **sem** alterar dados persistidos.

## precondicoes

- TASK-2 concluida (`done`): endpoint de escrita e validacao de negocio implementados.
- Mecanismo atual de autenticacao e autorizacao revisado (`get_current_user`, tipos de usuario, dependencias FastAPI).

## orquestracao

- `depends_on`: `T2`.
- `parallel_safe`: `false`.

## arquivos_a_ler_ou_tocar

- `backend/app/routers/ativos.py`
- `backend/app/core/auth.py`
- `backend/app/models/models.py` *(se permissoes estiverem no modelo `Usuario` ou relacionados)*
- `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md` *(sec. 2.6 e requisitos de perfil, trechos relevantes apenas)*

## passos_atomicos

1. Identificar ou introduzir dependencia FastAPI reutilizavel (ex.: `Depends` com verificacao de papel/permissao) para "configuracao de ativos por evento", alinhada aos perfis existentes no sistema; evitar duplicar logica dispersa.
2. Aplicar a dependencia **apenas** aos endpoints de escrita de configuracao introduzidos na TASK-2 (GET de leitura pode permanecer com regras de visibilidade ja usadas em ativos, conforme decisao de produto implicita na US — se leitura tambem for restrita, documentar no commit e alinhar com PRD).
3. Para usuario autenticado sem permissao: retornar 403 com codigo/mensagem estavel (padrao `raise_http_error`), sem abrir sessao de escrita ou sem commit.
4. Adicionar testes de integracao que provem ausencia de alteracao no banco apos 403 *(podem ser estendidos na TASK-4 se preferir consolidar)*.

## comandos_permitidos

- `cd backend && PYTHONPATH=<raiz>:<raiz>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_ativos_endpoints.py -q`
- `cd backend && ruff check app/routers/ativos.py app/core/auth.py`

## resultado_esperado

- Cliente sem permissao recebe 403 em tentativa de escrita; estado da configuracao inalterado.
- Cliente com permissao continua passando pela validacao de negocio da TASK-2.

## testes_ou_validacoes_obrigatorias

- Cenario automatizado: usuario sem papel adequado chama escrita e recebe 403.
- Verificacao de que contagem ou snapshot dos registros de configuracao nao muda apos o 403.

## stop_conditions

- Parar com `BLOQUEADO` se o PRD nao definir ou nao existir no codigo um criterio objetivo para "permissao de configuracao" (ex.: falta de campo, flag ou tabela de RBAC).
- Parar se a unica forma de testar exigir dados sensiveis reais; usar fixtures SQLite do projeto.
