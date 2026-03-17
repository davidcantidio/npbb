---
doc_id: "ISSUE-F3-02-002-Corrigir-Drift-Residual-do-Contrato-de-Conexao-no-Troubleshooting.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-16"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F3-02-002 - Corrigir drift residual do contrato de conexao no troubleshooting

## User Story

Como operador e mantenedor do projeto, quero corrigir o drift residual entre
`docs/TROUBLESHOOTING.md` e o contrato final de `DATABASE_URL`/`DIRECT_URL`,
para que o runbook de F3 nao reintroduza configuracao ambigua apos o cutover
para Supabase como banco unico.

## Contexto Tecnico

- issue de origem: `ISSUE-F3-02-001-Atualizar-Configuracao-e-Documentacao-para-Supabase-como-Banco-Unico`
- evidencia usada na revisao:
  - diff historico da issue de origem: `28cb55c`, `ff2b5ac`, `952e639`, `3af1f70`, `83ccbac`
  - estado atual de `backend/.env.example`, `docs/SETUP.md`, `docs/TROUBLESHOOTING.md`, `docs/DEPLOY_RENDER_CLOUDFLARE.md`, `docs/render.yaml`, `scripts/dev_backend.sh`
  - validacao `cd backend && PYTHONPATH=.. TESTING=true .venv/bin/python -c "from app.db.database import _get_database_url; print(_get_database_url())"` com retorno `sqlite:///./app.db`
  - validacao `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key .venv/bin/python -m pytest -q tests/test_alembic_single_head.py` com `1 passed`
- sintoma observado:
  - `docs/TROUBLESHOOTING.md` ainda mostra exemplo com `DATABASE_URL` e `DIRECT_URL` ambos em conexao direta `:5432`
  - o mesmo documento declara depois que `DATABASE_URL` deve ser usado no runtime e `DIRECT_URL` em migrations/seed, contrariando o proprio exemplo inicial
  - a T4 da issue de origem fechou a revisao final sem evidencia executavel cobrindo a coerencia cruzada entre `.env.example`, `SETUP.md` e `TROUBLESHOOTING.md`
- risco de nao corrigir:
  - operador pode configurar o runtime com URL direta por equivalencia indevida
  - o runbook volta a divergir do contrato documentado como estado final da F3
  - a fase pode seguir para auditoria com drift documental residual em um ponto de entrada operacional relevante

## Plano TDD

- Red: localizar os trechos de troubleshooting que contradizem o contrato consolidado em `.env.example` e `SETUP.md`
- Green: corrigir exemplos e instrucoes para deixar explicito o papel de `DATABASE_URL` no runtime e `DIRECT_URL` em migrations/seed
- Refactor: fechar uma validacao final curta e repetivel para evitar regressao documental local antes de encerrar a issue

## Criterios de Aceitacao

- Given `docs/TROUBLESHOOTING.md`, When o operador consultar o item de configuracao de banco, Then o exemplo deixa explicito `DATABASE_URL` como runtime e `DIRECT_URL` como conexao direta para operacoes sensiveis sem usar `:5432` de forma indiferenciada nas duas variaveis
- Given `backend/.env.example` e `docs/SETUP.md`, When a revisao final da issue for executada, Then `docs/TROUBLESHOOTING.md` fica coerente com o mesmo contrato documental da F3
- Given a issue concluida, When as validacoes obrigatorias forem rodadas, Then o fallback SQLite em testes continua preservado e a coerencia documental local fica evidenciada

## Definition of Done da Issue

- [ ] `docs/TROUBLESHOOTING.md` corrigido no trecho residual de contrato de conexao
- [ ] validacao final confirma coerencia entre `backend/.env.example`, `docs/SETUP.md` e `docs/TROUBLESHOOTING.md`
- [ ] fallback SQLite em testes revalidado sem regressao

## Tasks

- [T1: Corrigir o trecho residual de contrato em `docs/TROUBLESHOOTING.md`](./TASK-1.md)
- [T2: Validar coerencia final entre env, setup e troubleshooting](./TASK-2.md)

## Arquivos Reais Envolvidos

- `docs/TROUBLESHOOTING.md`
- `backend/.env.example`
- `docs/SETUP.md`
- `backend/app/db/database.py`

## Artifact Minimo

Trecho de troubleshooting alinhado ao contrato final de `DATABASE_URL` e
`DIRECT_URL`, com validacao final local registrada na execucao da issue.

## Dependencias

- [Intake](../../../INTAKE-SUPABASE.md)
- [PRD](../../../PRD-SUPABASE.md)
- [Fase](../../F3_SUPABASE_EPICS.md)
- [Epic](../../EPIC-F3-02-Consolidar-Configuracao-Final-e-Remover-Dependencia-do-Postgres-Local.md)
- [ISSUE-F3-02-001](../ISSUE-F3-02-001-Atualizar-Configuracao-e-Documentacao-para-Supabase-como-Banco-Unico/)
