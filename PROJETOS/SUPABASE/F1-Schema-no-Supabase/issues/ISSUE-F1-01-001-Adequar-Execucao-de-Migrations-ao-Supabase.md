---
doc_id: "ISSUE-F1-01-001-Adequar-Execucao-de-Migrations-ao-Supabase.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-16"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-01-001 - Adequar execucao de migrations ao Supabase

## User Story

Como operador do backend, quero que o fluxo de migrations use o contrato certo
de conexao para o Supabase, para aplicar schema com `DIRECT_URL` sem quebrar o
fallback existente de runtime e testes.

## Contexto Tecnico

`backend/alembic/env.py` ja prioriza `DIRECT_URL`, mas o wrapper
`backend/scripts/migrate.ps1` ainda assume somente `DATABASE_URL`. A issue deve
alinhar o fluxo Alembic ao contrato do PRD: `DIRECT_URL` para migrations, com
fallback controlado para `DATABASE_URL`, sem regressao no fallback SQLite de
`backend/app/db/database.py`.

## Plano TDD
- Red: expor o gap entre os entrypoints atuais e o contrato de migrations do Supabase
- Green: alinhar a resolucao de URLs e as mensagens de erro ao fluxo `DIRECT_URL` primeiro
- Refactor: reduzir duplicacao entre wrappers e documentar o contrato no proprio codigo quando necessario

## Criterios de Aceitacao
- Given `DIRECT_URL` definida, When o fluxo Alembic e executado, Then a conexao direta e a opcao prioritaria para migrations
- Given apenas `DATABASE_URL` definida, When o fluxo Alembic e executado, Then o fallback continua funcional sem bloquear o operador
- Given ambiente de teste com SQLite, When as validacoes minimas do backend rodam, Then o comportamento de testes nao regride

## Definition of Done da Issue
- [x] entrypoints de migrations alinhados ao contrato do Supabase
- [x] mensagens de erro e fallback coerentes com `DIRECT_URL` e `DATABASE_URL`
- [x] validacao minima sem regressao no fluxo de testes

## Tasks Decupadas
- [x] T1: mapear a resolucao atual de URLs no fluxo Alembic e seus pontos de divergencia
- [x] T2: ajustar os entrypoints de migrations para refletir `DIRECT_URL` primeiro e `DATABASE_URL` como fallback
- [x] T3: validar mensagens de erro e cobertura minima sem regressao de testes

## Instructions por Task

### T1
- objetivo: identificar exatamente onde o contrato de URLs de migrations diverge do PRD e do comportamento esperado no Supabase
- precondicoes: leitura do PRD concluida; acesso aos arquivos de configuracao e scripts existente
- arquivos_a_ler_ou_tocar:
  - `backend/alembic/env.py`
  - `backend/scripts/migrate.ps1`
  - `backend/app/db/database.py`
  - `backend/.env.example`
- passos_atomicos:
  1. revisar em `backend/alembic/env.py` a ordem atual de resolucao entre `DIRECT_URL` e `DATABASE_URL`
  2. revisar em `backend/scripts/migrate.ps1` quais variaveis o wrapper aceita hoje para rodar `alembic upgrade head`
  3. comparar esse fluxo com o fallback de runtime em `backend/app/db/database.py` para garantir que o ajuste de migrations nao interfira no comportamento de aplicacao e testes
  4. registrar os gaps objetivos que precisam ser corrigidos nesta issue
- comandos_permitidos:
  - `rg -n "DIRECT_URL|DATABASE_URL" backend/alembic/env.py backend/scripts/migrate.ps1 backend/app/db/database.py backend/.env.example`
- resultado_esperado: divergencias entre fluxo Alembic e contrato do Supabase mapeadas de forma objetiva
- testes_ou_validacoes_obrigatorias:
  - confirmar que o mapeamento cobre `env.py`, wrapper e fallback de runtime
- stop_conditions:
  - parar se surgir dependencia de arquivos fora do backend que altere o contrato de conexao

### T2
- objetivo: alinhar o fluxo de execucao de migrations ao contrato `DIRECT_URL` primeiro, mantendo fallback controlado
- precondicoes: T1 concluida; pontos de divergencia definidos
- arquivos_a_ler_ou_tocar:
  - `backend/alembic/env.py`
  - `backend/scripts/migrate.ps1`
  - `backend/.env.example`
- passos_atomicos:
  1. ajustar o wrapper de migrations para aceitar o contrato de `DIRECT_URL` e fallback para `DATABASE_URL` sem contradizer `backend/alembic/env.py`
  2. manter clara a separacao entre URL de migrations e URL de runtime, sem alterar o comportamento esperado em producao
  3. revisar o contrato exposto em `backend/.env.example` apenas se o alinhamento do fluxo exigir ajuste de nomenclatura ou observacao tecnica
  4. garantir que o resultado nao introduza dependencia de Supabase Auth ou qualquer alteracao fora do escopo do PRD
- comandos_permitidos:
  - `cd backend && alembic upgrade head`
- resultado_esperado: fluxo de migrations coerente com `DIRECT_URL` no Supabase e fallback controlado para `DATABASE_URL`
- testes_ou_validacoes_obrigatorias:
  - verificar que o codigo continua permitindo fallback explicito quando `DIRECT_URL` nao estiver disponivel
- stop_conditions:
  - parar se o ajuste exigir mudar o contrato de runtime do backend ou alterar o fallback SQLite de testes

### T3
- objetivo: confirmar que o ajuste do fluxo de migrations nao regrediu a validacao minima do backend
- precondicoes: T2 concluida; fluxo ajustado
- arquivos_a_ler_ou_tocar:
  - `backend/tests/test_alembic_single_head.py`
  - `backend/alembic.ini`
  - `backend/alembic/env.py`
- passos_atomicos:
  1. revisar se `backend/tests/test_alembic_single_head.py` continua refletindo a expectativa minima do historico Alembic
  2. executar a validacao automatizada minima relacionada ao historico de migrations
  3. confirmar que as mensagens de erro do fluxo ajustado permanecem objetivas quando faltarem `DIRECT_URL` e `DATABASE_URL`
  4. consolidar o resultado para liberar a issue seguinte de validacao contra o Supabase
- comandos_permitidos:
  - `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python -m pytest -q tests/test_alembic_single_head.py`
- resultado_esperado: validacao minima verde e fluxo de migrations pronto para ser exercitado no Supabase
- testes_ou_validacoes_obrigatorias:
  - `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python -m pytest -q tests/test_alembic_single_head.py`
- stop_conditions:
  - parar se aparecer mais de um head Alembic ou se o ajuste de execucao alterar o caminho de testes SQLite

## Arquivos Reais Envolvidos
- `backend/alembic/env.py`
- `backend/scripts/migrate.ps1`
- `backend/app/db/database.py`
- `backend/.env.example`
- `backend/tests/test_alembic_single_head.py`
- `backend/alembic.ini`

## Artifact Minimo

Fluxo de migrations coerente com `DIRECT_URL` para o Supabase, fallback claro
para `DATABASE_URL` e validacao minima preservada.

## Dependencias
- [Intake](../../INTAKE-SUPABASE.md)
- [Epic](../EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md)
- [Fase](../F1_SUPABASE_EPICS.md)
- [PRD](../../PRD-SUPABASE.md)
