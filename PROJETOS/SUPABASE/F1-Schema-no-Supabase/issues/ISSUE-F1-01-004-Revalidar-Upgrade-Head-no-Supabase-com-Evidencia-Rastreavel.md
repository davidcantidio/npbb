---
doc_id: "ISSUE-F1-01-004-Revalidar-Upgrade-Head-no-Supabase-com-Evidencia-Rastreavel.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-16"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-01-004 - Revalidar upgrade head no Supabase com evidencia rastreavel

## User Story

Como operador de deploy, quero revalidar o `alembic upgrade head` no Supabase
com evidencia objetiva do uso de `DIRECT_URL`, para liberar a F2 apenas sobre um
schema comprovadamente alinhado ao head atual do repositorio.

## Contexto Tecnico

A revisao pos-issue da `ISSUE-F1-01-002` encontrou dois problemas materiais no
fechamento anterior: nao ha evidencia auditavel da rodada real de
`alembic upgrade head` no Supabase e o fluxo atual ainda permite ambiguidade
entre `DIRECT_URL` e `DATABASE_URL`, o que pode mascarar um falso positivo de
validacao.

Rastreabilidade obrigatoria desta issue:
- issue de origem: `ISSUE-F1-01-002`
- evidencia usada na revisao: `BASE_COMMIT=worktree`, `git status --short`,
  `git diff --stat`, leitura de `backend/alembic/env.py`,
  `backend/scripts/migrate.ps1`, `backend/tests/test_alembic_single_head.py` e
  `docs/TROUBLESHOOTING.md`, alem da reexecucao de
  `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python3 -m pytest -q tests/test_alembic_single_head.py`
- sintoma observado: o estado atual so comprova head unico local; nao comprova,
  com log verificavel, que o Supabase chegou ao head via conexao direta
- risco de nao corrigir: a F2 pode iniciar sobre um schema nao comprovado e a
  trilha operacional continua sem prova objetiva do uso de `DIRECT_URL`

Esta issue e dependente de `ISSUE-F1-01-003`, porque a revalidacao so e
confiavel quando o fluxo de migrations deixar de aceitar fallback silencioso
para `DATABASE_URL` no caminho de validacao do Supabase.

## Plano TDD

- Red: falhar cedo se `DIRECT_URL` nao estiver obrigatoria no caminho de
  validacao ou se nao houver como provar a revision final aplicada no Supabase
- Green: executar `alembic upgrade head` no Supabase, confirmar a revision
  final `a7b8c9d0e1f2` e registrar evidencias objetivas da rodada
- Refactor: consolidar a evidencia minima para auditoria e atualizar
  troubleshooting apenas se surgir bloqueio operacional objetivo e recorrente

## Criterios de Aceitacao

- Given `ISSUE-F1-01-003` concluida e o head local esperado em
  `a7b8c9d0e1f2`, When a revalidacao for preparada, Then o fluxo operacional
  usado para o Supabase nao pode validar com fallback silencioso para
  `DATABASE_URL`
- Given `DIRECT_URL` valida para o ambiente alvo, When `alembic upgrade head`
  rodar contra o Supabase, Then o comando conclui sem erro e o ambiente alvo
  fica na revision `a7b8c9d0e1f2`
- Given a rodada concluida, When a issue for encerrada, Then a evidencia minima
  registra o comando executado, o uso de `DIRECT_URL`, o resultado de
  `alembic current` e o resultado da verificacao automatizada de head unico

## Definition of Done da Issue

- [ ] `ISSUE-F1-01-003` concluida ou bloqueio explicitado
- [ ] rodada real de `alembic upgrade head` executada no Supabase com
      `DIRECT_URL`
- [ ] revision final observada no ambiente alvo registrada com evidencia minima
- [ ] verificacao automatizada de head unico reexecutada com sucesso
- [ ] status de prontidao para F2 declarado sem inferencia

## Tasks Decupadas

- [ ] T1: confirmar as pre-condicoes da revalidacao e o contrato estrito de URLs
- [ ] T2: executar a rodada real de `alembic upgrade head` no Supabase
- [ ] T3: validar a revision final aplicada e o historico Alembic local
- [ ] T4: consolidar a evidencia rastreavel para liberar ou bloquear a F2

## Instructions por Task

### T1
- objetivo: garantir que a nova rodada nao repita o falso positivo da issue de origem
- precondicoes: `ISSUE-F1-01-002` concluida; `ISSUE-F1-01-003` concluida;
  acesso controlado a `DIRECT_URL` e `DATABASE_URL`
- arquivos_a_ler_ou_tocar:
  - `backend/alembic/env.py`
  - `backend/scripts/migrate.ps1`
  - `backend/tests/test_alembic_single_head.py`
  - `backend/alembic/versions/`
- passos_atomicos:
  1. confirmar que o fluxo operacional a ser usado na revalidacao exige
     `DIRECT_URL` para o caminho de migrations do Supabase ou falha cedo em vez
     de validar silenciosamente com `DATABASE_URL`
  2. confirmar que o head local esperado continua em `a7b8c9d0e1f2`
  3. reexecutar a verificacao automatizada minima de head unico
  4. parar imediatamente se `ISSUE-F1-01-003` ainda estiver pendente, se houver
     mais de um head ou se o fluxo ainda permitir validacao ambigua
- comandos_permitidos:
  - `cd backend && TESTING=true python3 -m alembic heads`
  - `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python3 -m pytest -q tests/test_alembic_single_head.py`
- resultado_esperado: revalidacao elegivel apenas com contrato de URLs
  coerente e head local confirmado
- testes_ou_validacoes_obrigatorias:
  - `cd backend && TESTING=true python3 -m alembic heads`
  - `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python3 -m pytest -q tests/test_alembic_single_head.py`
- stop_conditions:
  - parar se `ISSUE-F1-01-003` nao estiver `done`
  - parar se o head local nao for `a7b8c9d0e1f2`
  - parar se o fluxo de validacao ainda aceitar fallback silencioso para
    `DATABASE_URL`

### T2
- objetivo: executar a rodada real de upgrade no Supabase com prova objetiva do uso de `DIRECT_URL`
- precondicoes: T1 concluida; `DIRECT_URL` e `DATABASE_URL` explicitamente definidas
- arquivos_a_ler_ou_tocar:
  - `backend/alembic/env.py`
  - `backend/scripts/migrate.ps1`
  - `backend/alembic/versions/`
- passos_atomicos:
  1. preparar o ambiente com `DIRECT_URL` explicitamente definida para a rodada
     de migrations
  2. executar `alembic upgrade head` contra o Supabase sem alterar manualmente
     o schema fora do historico Alembic
  3. registrar o comando executado, o resultado bruto e a revision final
     observada ao termino
  4. parar no ponto exato de falha se houver erro, timeout ou sintoma de uso do
     pooler em vez da conexao direta
- comandos_permitidos:
  - `cd backend && DIRECT_URL="$DIRECT_URL" DATABASE_URL="$DATABASE_URL" alembic upgrade head`
- resultado_esperado: ambiente alvo alcanca `a7b8c9d0e1f2` por uma rodada real
  de migrations com `DIRECT_URL`
- testes_ou_validacoes_obrigatorias:
  - confirmar que o comando concluiu sem erro
  - confirmar que a rodada produz evidencia objetiva do uso de `DIRECT_URL`
- stop_conditions:
  - parar se a execucao exigir ajuste manual fora do historico Alembic
  - parar se houver indicio objetivo de que a validacao ocorreu pelo caminho errado
  - parar se a revision final nao puder ser determinada com seguranca

### T3
- objetivo: validar que o Supabase e o historico local ficaram alinhados ao mesmo head
- precondicoes: T2 concluida com sucesso
- arquivos_a_ler_ou_tocar:
  - `backend/alembic/env.py`
  - `backend/alembic/versions/`
  - `backend/tests/test_alembic_single_head.py`
  - `docs/TROUBLESHOOTING.md`
- passos_atomicos:
  1. consultar a revision atual do ambiente alvo apos o upgrade
  2. comparar a revision do ambiente alvo com o head local esperado
     `a7b8c9d0e1f2`
  3. reexecutar a verificacao automatizada minima de head unico no repositorio
  4. registrar qualquer anomalia objetiva de conexao, timeout ou ordem de
     migrations apenas se ela for reproduzivel e relevante para a proxima fase
- comandos_permitidos:
  - `cd backend && DIRECT_URL="$DIRECT_URL" DATABASE_URL="$DATABASE_URL" alembic current`
  - `cd backend && TESTING=true python3 -m alembic heads`
  - `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python3 -m pytest -q tests/test_alembic_single_head.py`
- resultado_esperado: ambiente alvo e historico local alinhados a
  `a7b8c9d0e1f2`
- testes_ou_validacoes_obrigatorias:
  - `cd backend && DIRECT_URL="$DIRECT_URL" DATABASE_URL="$DATABASE_URL" alembic current`
  - `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python3 -m pytest -q tests/test_alembic_single_head.py`
- stop_conditions:
  - parar se `alembic current` nao confirmar a mesma revision do head local
  - parar se a verificacao automatizada minima falhar

### T4
- objetivo: consolidar a evidencia minima e declarar com clareza se a F2 pode iniciar
- precondicoes: T3 concluida
- arquivos_a_ler_ou_tocar:
  - `backend/alembic/env.py`
  - `backend/scripts/migrate.ps1`
  - `backend/tests/test_alembic_single_head.py`
  - `docs/TROUBLESHOOTING.md`
- passos_atomicos:
  1. registrar a evidencia minima desta rodada com os comandos executados, uso
     de `DIRECT_URL`, resultado de `alembic current`, head esperado e resultado
     do teste automatizado
  2. declarar explicitamente se a F2 esta liberada ou se ainda existe bloqueio
     objetivo
  3. atualizar `docs/TROUBLESHOOTING.md` apenas se a rodada revelar um sintoma
     recorrente com correcao canonica e objetiva
  4. encerrar a issue apenas quando a evidencia estiver suficiente para auditoria
     posterior sem depender de memoria da sessao
- comandos_permitidos:
  - `rg -n "DIRECT_URL|DATABASE_URL|pooler|5432|6543" docs/TROUBLESHOOTING.md backend/alembic/env.py backend/scripts/migrate.ps1`
- resultado_esperado: evidencia rastreavel suficiente para julgamento de
  prontidao da F2
- testes_ou_validacoes_obrigatorias:
  - confirmar que o resumo final inclui comando executado, revision final
    observada, saida de `alembic current` e resultado do teste de head unico
- stop_conditions:
  - parar se a evidencia final ainda depender de inferencia
  - parar se houver bloqueio objetivo nao documentado

## Arquivos Reais Envolvidos

- `backend/alembic/env.py`
- `backend/scripts/migrate.ps1`
- `backend/alembic/versions/`
- `backend/tests/test_alembic_single_head.py`
- `docs/TROUBLESHOOTING.md`

## Artifact Minimo

Registro tecnico rastreavel da rodada real de `alembic upgrade head` no
Supabase, incluindo uso de `DIRECT_URL`, revision final `a7b8c9d0e1f2`,
resultado de `alembic current` e resultado da validacao automatizada minima.

## Dependencias

- [Intake](../../INTAKE-SUPABASE.md)
- [Epic](../EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md)
- [Fase](../F1_SUPABASE_EPICS.md)
- [PRD](../../PRD-SUPABASE.md)
- [ISSUE-F1-01-002](./ISSUE-F1-01-002-Validar-Schema-do-Supabase-com-Alembic-Upgrade-Head.md)
- [ISSUE-F1-01-003](./ISSUE-F1-01-003-Endurecer-Fallback-de-URLs-no-Fluxo-Alembic.md)
