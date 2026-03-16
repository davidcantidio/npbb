---
doc_id: "ISSUE-F2-02-003-Endurecer-Contratos-e-Atomicidade-da-Recarga-no-Supabase.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-16"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-02-003 - Endurecer contratos e atomicidade da recarga no Supabase

## User Story

Como operador da migracao, quero que a automacao de recarga bloqueie artefatos
incompativeis, falhe de forma atomica e nao declare prontidao antes da hora,
para evitar carga parcial e falso positivo antes da validacao pos-carga.

## Contexto Tecnico

Esta issue nasce da revisao pos-issue da
`ISSUE-F2-02-001-Implementar-Recarga-Controlada-de-Dados-no-Supabase.md`.

- issue de origem: `ISSUE-F2-02-001`
- evidencia usada na revisao:
  - diff dos commits `4b91fc3`, `3d078be`, `5d50a57`, `24961db`, `315e3c0`
  - leitura de `backend/scripts/backup_export_migracao.py`
  - leitura de `backend/scripts/recarga_migracao.py`
  - leitura de `backend/app/db/database.py`
  - leitura de `docs/RUNBOOK-MIGRACAO-SUPABASE.md`
  - verificacao local de `pg_restore --help` e `pg_dump --help`
  - ausencia de testes especificos para os scripts de migracao em `backend/tests`
- sintoma observado:
  - o export local ainda pode alimentar a recarga com dados de `alembic_version`
  - a importacao via `pg_restore` nao esta configurada para parar no primeiro erro nem para rodar em transacao unica
  - a consolidacao valida apenas a conexao direta de manutencao e pode liberar falso positivo para a etapa seguinte
- risco de nao corrigir:
  - a recarga pode falhar no caminho feliz por conflito com `alembic_version`
  - o Supabase pode ficar parcialmente truncado/carregado em caso de falha durante a importacao
  - a `ISSUE-F2-02-002` pode receber um ambiente marcado como pronto sem o contrato minimo de runtime estar objetivamente apto

## Plano TDD
- Red: reproduzir via testes o dump incompativel, a carga parcial e o falso positivo de prontidao
- Green: endurecer o contrato do artefato, a importacao atomica e a consolidacao de prontidao
- Refactor: consolidar helpers e mensagens operacionais sem alterar o escopo funcional do epico

## Criterios de Aceitacao
- Given um export local em formato custom, When a recarga selecionar o artefato, Then a automacao bloqueia qualquer dump que ainda contenha dados de `alembic_version` antes de qualquer passo destrutivo
- Given uma falha durante `pg_restore`, When a importacao rodar, Then a automacao interrompe a rodada na primeira falha e nao deixa a carga seguir sem garantia de atomicidade
- Given a recarga concluida pela conexao direta, When a consolidacao rodar, Then ela so libera a proxima etapa quando o contrato de runtime estiver objetivamente apto; caso contrario, ela bloqueia com mensagem clara
- Given o follow-up concluido, When os checks locais rodarem, Then existem testes automatizados cobrindo o contrato corrigido dos scripts de migracao

## Definition of Done da Issue
- [x] export e pre-validacao da recarga impedem artefato incompativel com o schema validado em F1
- [x] `pg_restore` roda em modo fail-fast e atomico para a carga de dados
- [x] a consolidacao nao declara prontidao para `ISSUE-F2-02-002` sem validar o contrato correto
- [x] testes automatizados locais cobrem os ajustes desta issue

## Tasks Decupadas
- [x] T1: endurecer o contrato do artefato de export e da pre-validacao da recarga
- [x] T2: tornar a importacao via `pg_restore` fail-fast e atomica
- [x] T3: alinhar a consolidacao com a prontidao real para a `ISSUE-F2-02-002`
- [x] T4: cobrir o follow-up com testes e sincronizacao minima da documentacao

## Instructions por Task

### T1
- objetivo: impedir que a recarga consuma dump incompativel com o schema ja validado em F1
- precondicoes: `ISSUE-F2-02-001` concluida; scripts atuais legiveis; sem executar limpeza/import real durante a implementacao
- arquivos_a_ler_ou_tocar:
  - `backend/scripts/backup_export_migracao.py`
  - `backend/scripts/recarga_migracao.py`
  - `docs/RUNBOOK-MIGRACAO-SUPABASE.md`
- passos_atomicos:
  1. ajustar o comando de export local para nao incluir dados de `public.alembic_version` no dump custom
  2. adicionar uma verificacao reproduzivel na pre-validacao da recarga para inspecionar o artefato selecionado antes da limpeza
  3. bloquear a recarga se o dump ainda contiver `alembic_version` ou outro sinal objetivo de contrato incompativel com o schema aprovado em F1
  4. manter o bloqueio sempre antes do primeiro passo destrutivo no Supabase
- comandos_permitidos:
  - `pg_dump --help`
  - `pg_restore --help`
- resultado_esperado: apenas artefatos compativeis sao aceitos para a recarga
- testes_ou_validacoes_obrigatorias:
  - teste automatizado que valide os argumentos do `pg_dump` no export local
  - teste automatizado que valide o bloqueio da recarga quando o artefato listar `alembic_version`
- stop_conditions:
  - parar se a verificacao do artefato exigir acesso destrutivo ao banco real ou mudanca de schema fora do escopo da fase

### T2
- objetivo: garantir que a importacao pare na primeira falha e preserve atomicidade da rodada
- precondicoes: T1 concluida; contrato do artefato endurecido
- arquivos_a_ler_ou_tocar:
  - `backend/scripts/recarga_migracao.py`
  - `docs/RUNBOOK-MIGRACAO-SUPABASE.md`
- passos_atomicos:
  1. atualizar a chamada de `pg_restore` para usar flags de parada imediata e transacao unica
  2. garantir que qualquer retorno diferente de zero interrompa a rodada sem mensagem de sucesso
  3. preservar `stdout` e `stderr` no erro para diagnostico objetivo
  4. alinhar a documentacao minima se o contrato operacional da importacao mudar
- comandos_permitidos:
  - `pg_restore --help`
- resultado_esperado: a carga de dados falha de forma explicita e atomica
- testes_ou_validacoes_obrigatorias:
  - teste automatizado que valide a presenca das flags de atomicidade na chamada de `pg_restore`
  - teste automatizado que valide o erro imediato em retorno nao zero
- stop_conditions:
  - parar se a abordagem escolhida exigir mudar o formato dos artefatos ou introduzir restore destrutivo fora do escopo desta issue

### T3
- objetivo: impedir falso positivo de prontidao apos a recarga
- precondicoes: T2 concluida; importacao e consolidacao atuais compreendidas
- arquivos_a_ler_ou_tocar:
  - `backend/scripts/recarga_migracao.py`
  - `backend/app/db/database.py`
  - `backend/.env.example`
  - `docs/RUNBOOK-MIGRACAO-SUPABASE.md`
- passos_atomicos:
  1. separar explicitamente no script o contrato de manutencao (`SUPABASE_DIRECT_URL` ou `DIRECT_URL`) do contrato de runtime (`DATABASE_URL`)
  2. durante a consolidacao, validar o caminho de runtime quando ele estiver configurado para o Supabase
  3. se o runtime ainda estiver ausente ou apontando para caminho que mantenha dependencia operacional do PostgreSQL local, bloquear a liberacao da `ISSUE-F2-02-002` com mensagem objetiva em vez de declarar sucesso
  4. ajustar comentarios e mensagens para refletir com precisao o que foi validado e o que ainda bloqueia a proxima etapa
- comandos_permitidos:
  - `rg -n "DATABASE_URL|DIRECT_URL" backend/app/db/database.py backend/.env.example`
- resultado_esperado: a consolidacao so comunica prontidao quando o contrato correto estiver objetivamente apto
- testes_ou_validacoes_obrigatorias:
  - teste automatizado para o caminho de sucesso quando `DATABASE_URL` estiver apta
  - teste automatizado para o bloqueio quando apenas a conexao direta estiver valida
- stop_conditions:
  - parar se a correcao exigir reescopo de F3 ou mudanca de contrato fora do epico atual

### T4
- objetivo: fechar cobertura automatizada e manter a documentacao minima coerente com o comportamento corrigido
- precondicoes: T1, T2 e T3 concluidas
- arquivos_a_ler_ou_tocar:
  - `backend/tests/test_migracao_scripts.py`
  - `backend/scripts/backup_export_migracao.py`
  - `backend/scripts/recarga_migracao.py`
  - `docs/RUNBOOK-MIGRACAO-SUPABASE.md`
  - `backend/.env.example`
- passos_atomicos:
  1. concentrar em um modulo de teste os cenarios de artefato incompativel, restore atomico e prontidao de runtime
  2. executar os checks locais declarados nesta issue
  3. revisar as mensagens finais e a documentacao minima para evitar overclaim sobre a prontidao da fase
  4. liberar a issue apenas com testes verdes e sem contradicao entre script e runbook
- comandos_permitidos:
  - `backend/.venv/bin/python -m py_compile backend/scripts/backup_export_migracao.py backend/scripts/recarga_migracao.py`
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_migracao_scripts.py`
- resultado_esperado: cobertura local suficiente para sustentar a correcao sem depender de carga real no Supabase
- testes_ou_validacoes_obrigatorias:
  - `backend/.venv/bin/python -m py_compile backend/scripts/backup_export_migracao.py backend/scripts/recarga_migracao.py`
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_migracao_scripts.py`
- stop_conditions:
  - parar se os testes exigirem credenciais reais do Supabase ou operacao destrutiva fora do escopo desta issue

## Arquivos Reais Envolvidos
- `backend/scripts/backup_export_migracao.py`
- `backend/scripts/recarga_migracao.py`
- `backend/app/db/database.py`
- `backend/.env.example`
- `docs/RUNBOOK-MIGRACAO-SUPABASE.md`
- `backend/tests/test_migracao_scripts.py`

## Artifact Minimo

Automacao de migracao endurecida contra dump incompativel, carga parcial e falso
positivo de prontidao, com cobertura automatizada local para os contratos
corrigidos.

**Artifacts gerados/atualizados:**
- `backend/scripts/backup_export_migracao.py`
- `backend/scripts/recarga_migracao.py`
- `backend/tests/test_migracao_scripts.py`

## Dependencias
- [Intake](../../INTAKE-SUPABASE.md)
- [Epic](../EPIC-F2-02-Recarregar-o-Supabase-com-os-Dados-Locais.md)
- [Fase](../F2_SUPABASE_EPICS.md)
- [PRD](../../PRD-SUPABASE.md)
- [ISSUE-F2-02-001](./ISSUE-F2-02-001-Implementar-Recarga-Controlada-de-Dados-no-Supabase.md)
- [ISSUE-F2-01-002](./ISSUE-F2-01-002-Automatizar-Backup-do-Supabase-e-Export-do-PostgreSQL-Local.md)
