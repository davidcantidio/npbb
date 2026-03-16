---
doc_id: "ISSUE-F1-01-002-Validar-Schema-do-Supabase-com-Alembic-Upgrade-Head.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-16"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-01-002 - Validar schema do Supabase com Alembic upgrade head

## User Story

Como operador de deploy, quero validar que `alembic upgrade head` aplica o
schema atual no Supabase, para iniciar a migracao de dados sobre um ambiente
alvo alinhado ao estado local do projeto.

## Contexto Tecnico

O repositorio possui 50 migrations Alembic em `backend/alembic/versions/` e um
teste de head unico em `backend/tests/test_alembic_single_head.py`. Esta issue
nao cria novos requisitos de schema: ela comprova que o historico atual sobe no
Supabase usando `DIRECT_URL`, com evidencia suficiente para liberar F2.

## Plano TDD
- Red: falhar cedo se houver head duplicado, credenciais ausentes ou erro na subida do schema
- Green: executar `alembic upgrade head` com `DIRECT_URL` valida e confirmar o estado final
- Refactor: consolidar a evidencia tecnica minima para a liberacao da fase seguinte

## Criterios de Aceitacao
- Given credenciais validas de `DIRECT_URL` e `DATABASE_URL`, When `alembic upgrade head` roda contra o Supabase, Then o comando conclui sem erro
- Given o upgrade concluido, When as verificacoes minimas do historico Alembic rodam, Then o projeto permanece com um unico head e sem drift evidente
- Given a validacao encerrada, When F2 for iniciada, Then existe evidencia tecnica objetiva do schema aplicado no Supabase

## Definition of Done da Issue
- [x] pre-condicoes de migrations revisadas antes da execucao no Supabase
- [x] `alembic upgrade head` executado com sucesso no ambiente alvo
- [x] evidencia tecnica consolidada para liberar a fase F2

## Tasks Decupadas
- [x] T1: revisar pre-condicoes do historico Alembic e do ambiente alvo
- [x] T2: executar `alembic upgrade head` no Supabase com as URLs corretas
- [x] T3: validar o estado final do schema e do historico Alembic
- [x] T4: consolidar a evidencia minima e registrar bloqueios objetivos, se houver

## Instructions por Task

### T1
- objetivo: garantir que o historico Alembic e o ambiente alvo estao aptos para uma validacao real no Supabase
- precondicoes: ISSUE-F1-01-001 concluida; acesso controlado a `DIRECT_URL` e `DATABASE_URL`
- arquivos_a_ler_ou_tocar:
  - `backend/alembic/env.py`
  - `backend/alembic.ini`
  - `backend/alembic/versions/`
  - `backend/tests/test_alembic_single_head.py`
- passos_atomicos:
  1. revisar o `env.py` e o `alembic.ini` para confirmar o caminho de execucao esperado para o Supabase
  2. confirmar que o historico em `backend/alembic/versions/` esta consistente com um unico head
  3. executar a validacao automatizada minima de head unico antes da subida real
  4. validar que as credenciais de `DIRECT_URL` e `DATABASE_URL` estao disponiveis explicitamente para a rodada
- comandos_permitidos:
  - `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python -m pytest -q tests/test_alembic_single_head.py`
- resultado_esperado: ambiente e historico Alembic aptos para a validacao real no Supabase
- testes_ou_validacoes_obrigatorias:
  - `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python -m pytest -q tests/test_alembic_single_head.py`
- stop_conditions:
  - parar se houver mais de um head Alembic ou se as credenciais do Supabase nao estiverem disponiveis

### T2
- objetivo: aplicar o schema atual no Supabase usando o fluxo Alembic alinhado ao contrato da F1
- precondicoes: T1 concluida; `DIRECT_URL` e `DATABASE_URL` explicitamente definidas
- arquivos_a_ler_ou_tocar:
  - `backend/alembic/env.py`
  - `backend/alembic/versions/`
  - `backend/scripts/migrate.ps1`
- passos_atomicos:
  1. preparar o ambiente de execucao com `DIRECT_URL` para migrations e `DATABASE_URL` para fallback controlado
  2. executar `alembic upgrade head` contra o Supabase
  3. observar o ponto exato de falha, se houver, sem introduzir alteracoes manuais fora do historico Alembic
  4. registrar a revision final aplicada e o resultado bruto da execucao
- comandos_permitidos:
  - `cd backend && DIRECT_URL=\"$DIRECT_URL\" DATABASE_URL=\"$DATABASE_URL\" alembic upgrade head`
- resultado_esperado: schema aplicado no Supabase ate a revision head atual
- testes_ou_validacoes_obrigatorias:
  - confirmar que o comando concluiu sem erro e alcancou o head esperado
- stop_conditions:
  - parar se uma migration exigir ajuste estrutural fora do escopo do PRD ou se houver risco de perda de dados no ambiente alvo

### T3
- objetivo: validar que o estado final do Supabase ficou coerente com o historico Alembic do repositorio
- precondicoes: T2 concluida com sucesso
- arquivos_a_ler_ou_tocar:
  - `backend/alembic/env.py`
  - `backend/alembic/versions/`
  - `backend/tests/test_alembic_single_head.py`
  - `docs/TROUBLESHOOTING.md`
- passos_atomicos:
  1. revisar a revision final esperada no historico Alembic local
  2. confirmar que o ambiente alvo chegou a mesma revision final depois do upgrade
  3. reexecutar a verificacao automatizada minima do historico para garantir que a base do repositorio continua coerente
  4. anotar qualquer anomalia objetiva de conexao, timeout ou ordem de migration para alimentar a fase seguinte
- comandos_permitidos:
  - `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python -m pytest -q tests/test_alembic_single_head.py`
- resultado_esperado: schema do Supabase alinhado ao head atual e historico Alembic local preservado
- testes_ou_validacoes_obrigatorias:
  - `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python -m pytest -q tests/test_alembic_single_head.py`
- stop_conditions:
  - parar se o head local nao corresponder ao estado final aplicado no Supabase

### T4
- objetivo: consolidar a evidencia minima para destravar a fase de migracao de dados
- precondicoes: T3 concluida
- arquivos_a_ler_ou_tocar:
  - `backend/alembic/env.py`
  - `backend/tests/test_alembic_single_head.py`
  - `docs/TROUBLESHOOTING.md`
- passos_atomicos:
  1. registrar os comandos executados, as premissas de ambiente e a revision final observada
  2. resumir se houve ou nao bloqueios objetivos para iniciar F2
  3. se existir falha, descrever a causa objetiva sem inventar workaround fora do escopo aprovado
  4. liberar a issue apenas quando a evidencia estiver suficiente para a migracao de dados
- comandos_permitidos:
  - `rg -n "DIRECT_URL|DATABASE_URL|Target database is not up to date|pooler" docs/TROUBLESHOOTING.md backend/alembic/env.py`
- resultado_esperado: evidencia de schema aplicado e checklist minimo pronto para F2
- testes_ou_validacoes_obrigatorias:
  - confirmar que o resumo inclui revision final, comando executado e estado da validacao minima
- stop_conditions:
  - parar se a evidencia nao conseguir afirmar com seguranca que F2 parte de um schema valido

## Arquivos Reais Envolvidos
- `backend/alembic/env.py`
- `backend/alembic.ini`
- `backend/alembic/versions/`
- `backend/scripts/migrate.ps1`
- `backend/tests/test_alembic_single_head.py`
- `docs/TROUBLESHOOTING.md`

## Artifact Minimo

Registro tecnico de que `alembic upgrade head` aplicou o schema atual no
Supabase e de que o historico Alembic permaneceu coerente.

## Dependencias
- [Intake](../../INTAKE-SUPABASE.md)
- [Epic](../EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md)
- [Fase](../F1_SUPABASE_EPICS.md)
- [PRD](../../PRD-SUPABASE.md)
- [ISSUE-F1-01-001](./ISSUE-F1-01-001-Adequar-Execucao-de-Migrations-ao-Supabase.md)
