---
doc_id: "ISSUE-F1-01-003-Endurecer-Fallback-de-URLs-no-Fluxo-Alembic.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-16"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-01-003 - Endurecer fallback de URLs no fluxo Alembic

## User Story

Como operador do backend, quero que o fluxo Alembic tente `DATABASE_URL` quando
`DIRECT_URL` falhar antes da conexao utilizavel, para nao perder a janela de
migracao por um erro de configuracao da URL direta e para manter o contrato de
fallback realmente executavel.

## Contexto Tecnico

A revisao pos-issue de `ISSUE-F1-01-001-Adequar-Execucao-de-Migrations-ao-Supabase.md`
usou como evidencia o estado atual de `backend/alembic/env.py`,
`backend/scripts/migrate.ps1`, `backend/tests/test_alembic_single_head.py`,
ausencia de diff relevante nesses arquivos no `worktree` e a execucao de
`python3 -m pytest -q tests/test_alembic_single_head.py` com resultado verde.

Sintoma observado:
- `backend/alembic/env.py` prioriza `DIRECT_URL`, mas o fallback para
  `DATABASE_URL` so acontece quando `connect()` falha com `OperationalError`
- falhas anteriores, como URL invalida, driver ausente ou erro de inicializacao
  do engine, interrompem o fluxo antes do fallback
- a cobertura automatizada atual verifica apenas que o historico Alembic possui
  um unico head, sem proteger o contrato de `DIRECT_URL` primeiro com fallback
  controlado

Risco de nao corrigir:
- uma `DIRECT_URL` malformada pode bloquear migrations mesmo com
  `DATABASE_URL` valida disponivel
- o operador recebe uma confianca falsa no fallback documentado
- regressao futura no contrato de URLs pode passar sem deteccao automatizada

## Plano TDD

- Red: reproduzir em teste o caso em que `DIRECT_URL` falha antes de entregar
  uma conexao utilizavel e o fallback esperado nao acontece
- Green: endurecer o loop de resolucao/abertura de conexao do Alembic para
  tentar `DATABASE_URL` apenas em falhas de preparacao/conexao, sem mascarar
  erro real de migration
- Refactor: isolar o trecho testavel do fluxo de conexao para manter o contrato
  explicito e coberto por regressao automatizada

## Criterios de Aceitacao

- Given `DIRECT_URL` e `DATABASE_URL` definidas, When a URL direta falhar antes
  do inicio efetivo das migrations, Then o fluxo Alembic tenta `DATABASE_URL`
  uma unica vez antes de falhar
- Given `DIRECT_URL` invalida e `DATABASE_URL` ausente, When o fluxo Alembic for
  executado, Then o erro final continua objetivo e deixa claro que nao ha rota
  valida para migrations
- Given a suite minima relacionada ao contrato de URLs, When os testes da issue
  rodarem, Then os cenarios de prioridade, fallback e erro sem URLs ficam
  cobertos sem regressao do teste de head unico
- Given uma falha real durante `context.run_migrations()`, When ela ocorrer apos
  a conexao ter sido aberta, Then o fluxo nao tenta fallback para outra URL e
  propaga o erro da migration

## Definition of Done da Issue

- [ ] fallback do Alembic cobre falhas de preparacao/conexao da `DIRECT_URL`
- [ ] erro de migration apos conexao aberta nao dispara fallback indevido
- [ ] cobertura automatizada protege prioridade, fallback e erro sem URLs
- [ ] contrato do runtime e do fallback SQLite de testes permanece inalterado

## Tasks Decupadas

- [ ] T1: delimitar o contrato de fallback e os pontos exatos em que ele pode ocorrer
- [ ] T2: endurecer a abertura de conexao do Alembic sem mascarar erro real de migration
- [ ] T3: adicionar cobertura de regressao para prioridade, fallback e mensagens de erro

## Instructions por Task

### T1
- objetivo: transformar o achado da revisao em um contrato executavel de
  fallback, sem reinterpretar o escopo da issue original
- precondicoes: issue de origem e revisao pos-issue lidas; acesso aos arquivos
  do fluxo Alembic e do fallback de runtime
- arquivos_a_ler_ou_tocar:
  - `backend/alembic/env.py`
  - `backend/scripts/migrate.ps1`
  - `backend/app/db/database.py`
  - `backend/tests/test_alembic_single_head.py`
- passos_atomicos:
  1. mapear no `backend/alembic/env.py` quais falhas acontecem antes de abrir a
     conexao e quais falhas acontecem depois do inicio efetivo da migration
  2. fixar como regra desta issue que o fallback entre URLs so e permitido ate
     a abertura de uma conexao utilizavel; depois disso, qualquer erro de
     migration deve ser propagado sem nova tentativa
  3. conferir em `backend/app/db/database.py` que nenhuma decisao desta issue
     muda o contrato de runtime nem o fallback SQLite de testes
  4. verificar se `backend/scripts/migrate.ps1` ja comunica corretamente que
     aceita `DIRECT_URL` e `DATABASE_URL`; se estiver coerente, manter o wrapper
     sem expandir escopo
- comandos_permitidos:
  - `rg -n "DIRECT_URL|DATABASE_URL|get_url|get_urls|run_migrations_online|OperationalError" backend/alembic/env.py backend/scripts/migrate.ps1 backend/app/db/database.py backend/tests`
- resultado_esperado: contrato de fallback delimitado com fronteira clara entre
  erro de conexao e erro real de migration
- testes_ou_validacoes_obrigatorias:
  - confirmar por leitura que o contrato de runtime em `backend/app/db/database.py`
    nao sera alterado
- stop_conditions:
  - parar se a correcao exigir mudar o comportamento de runtime da aplicacao ou
    o fallback SQLite fora do fluxo Alembic

### T2
- objetivo: corrigir o fluxo Alembic para que a tentativa de fallback seja
  realmente acionavel nas falhas certas e bloqueada nas falhas erradas
- precondicoes: T1 concluida; fronteira de fallback definida
- arquivos_a_ler_ou_tocar:
  - `backend/alembic/env.py`
  - `backend/scripts/migrate.ps1`
- passos_atomicos:
  1. ajustar `backend/alembic/env.py` para que a criacao do engine e a abertura
     da conexao acontecam dentro do trecho protegido pelo loop de URLs
  2. tratar como elegiveis para fallback apenas falhas de preparacao da URL,
     inicializacao do engine ou abertura de conexao antes da execucao das
     migrations
  3. manter a deduplicacao entre `DIRECT_URL` e `DATABASE_URL` para evitar
     segunda tentativa identica
  4. garantir que, apos a conexao ter sido aberta e `context.run_migrations()`
     iniciado, qualquer erro seja propagado sem fallback para outra URL
  5. tocar `backend/scripts/migrate.ps1` somente se a mensagem ou os parametros
     estiverem desalinhados com o contrato final; caso contrario, preservar o
     wrapper
- comandos_permitidos:
  - `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python3 -m pytest -q tests/test_alembic_single_head.py`
- resultado_esperado: fluxo Alembic resiliente a falhas pre-conexao da
  `DIRECT_URL`, sem esconder falhas reais de migration
- testes_ou_validacoes_obrigatorias:
  - verificar que o fallback entre URLs nao ocorre depois do inicio efetivo da
    migration
- stop_conditions:
  - parar se a unica forma de implementar o fallback exigir capturar excecoes
    de migration de forma indistinta, mascarando falhas reais do schema

### T3
- objetivo: criar cobertura de regressao suficiente para sustentar o fechamento
  da issue e impedir repeticao do problema
- precondicoes: T2 concluida; fluxo final estabilizado
- arquivos_a_ler_ou_tocar:
  - `backend/alembic/env.py`
  - `backend/tests/test_alembic_single_head.py`
  - `backend/tests/test_alembic_env_contract.py`
- passos_atomicos:
  1. adicionar um teste focado no contrato do Alembic cobrindo prioridade de
     `DIRECT_URL`, fallback para `DATABASE_URL` em falha pre-conexao e erro
     objetivo quando ambas estiverem indisponiveis
  2. adicionar um teste garantindo que falha ocorrida depois de abrir a conexao
     nao dispara fallback para outra URL
  3. manter `backend/tests/test_alembic_single_head.py` verde como protecao do
     historico Alembic existente
  4. executar a suite minima da issue e registrar o resultado apenas se todos os
     cenarios do contrato estiverem verificaveis por teste automatizado
- comandos_permitidos:
  - `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python3 -m pytest -q tests/test_alembic_single_head.py tests/test_alembic_env_contract.py`
- resultado_esperado: regressao automatizada cobrindo o contrato de URLs do
  fluxo Alembic sem depender de banco Supabase real
- testes_ou_validacoes_obrigatorias:
  - `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python3 -m pytest -q tests/test_alembic_single_head.py tests/test_alembic_env_contract.py`
- stop_conditions:
  - parar se a cobertura depender de infraestrutura externa real em vez de teste
    isolado do contrato do Alembic

## Arquivos Reais Envolvidos

- `backend/alembic/env.py`
- `backend/scripts/migrate.ps1`
- `backend/app/db/database.py`
- `backend/tests/test_alembic_single_head.py`
- `backend/tests/test_alembic_env_contract.py`

## Artifact Minimo

Fluxo Alembic com fallback de URLs endurecido para falhas pre-conexao e cobertura
automatizada de regressao para prioridade, fallback e erro sem URLs.

## Dependencias

- [Issue de Origem](./ISSUE-F1-01-001-Adequar-Execucao-de-Migrations-ao-Supabase.md)
- [Intake](../../INTAKE-SUPABASE.md)
- [Epic](../EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md)
- [Fase](../F1_SUPABASE_EPICS.md)
- [PRD](../../PRD-SUPABASE.md)
