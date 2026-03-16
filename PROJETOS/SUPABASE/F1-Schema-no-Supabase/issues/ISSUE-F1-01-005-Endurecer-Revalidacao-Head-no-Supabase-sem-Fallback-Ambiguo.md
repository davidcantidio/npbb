---
doc_id: "ISSUE-F1-01-005-Endurecer-Revalidacao-Head-no-Supabase-sem-Fallback-Ambiguo.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-16"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-01-005 - Endurecer revalidacao head no Supabase sem fallback ambiguo

## User Story

Como operador de deploy, quero um modo estrito de revalidacao do `alembic upgrade head`
no Supabase que aceite apenas `DIRECT_URL` e gere evidencia bruta da rodada,
para liberar a F2 sem ambiguidade sobre a rota realmente usada.

## Contexto Tecnico

Esta issue nasce da revisao pos-issue de `ISSUE-F1-01-004`.

Rastreabilidade obrigatoria desta issue:
- issue de origem: `ISSUE-F1-01-004`
- evidencia usada na revisao: `BASE_COMMIT=worktree`, `git status --short`,
  `git diff --stat`, leitura de
  `PROJETOS/SUPABASE/F1-Schema-no-Supabase/EVIDENCIA-F1-01-004-Revalidacao-Supabase.md`,
  `backend/alembic/env.py`, `backend/scripts/migrate.ps1`,
  `backend/tests/test_alembic_single_head.py`,
  `backend/tests/test_alembic_env_contract.py`,
  alem da reexecucao de
  `cd backend && TESTING=true python3 -m alembic heads`
  e
  `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python3 -m pytest -q tests/test_alembic_single_head.py`
- sintoma observado: a revalidacao da `ISSUE-F1-01-004` foi encerrada como
  concluida, mas o caminho operacional ainda pode cair em fallback pre-conexao
  para `DATABASE_URL`, e o artefato de evidencia atual confirma `DIRECT_URL`
  apenas por inferencia do comando e da prioridade do codigo, sem preservar
  saida bruta suficiente para provar a rota usada
- risco de nao corrigir: a F2 pode seguir liberada sobre uma validacao cuja
  conexao efetiva nao esta comprovada como direta; revisoes futuras continuam
  incapazes de diferenciar sucesso via `DIRECT_URL` de sucesso via fallback
  para `DATABASE_URL`

Escopo desta correcao:
- manter o contrato padrao do Alembic entregue em `ISSUE-F1-01-003`
  inalterado quando o modo estrito nao estiver ativo
- adicionar um modo explicito de revalidacao estrita do Supabase para
  `alembic upgrade head` e `alembic current`
- rerodar a revalidacao com evidencia objetiva e rastreavel

## Plano TDD

- Red: reproduzir em teste que a revalidacao estrita ainda aceitaria
  `DATABASE_URL` ou nao bloquearia a ausencia de `DIRECT_URL`
- Green: adicionar um modo explicito `ALEMBIC_STRICT_DIRECT_URL=true` no fluxo
  Alembic para que a revalidacao use somente `DIRECT_URL` e falhe cedo se ela
  nao estiver disponivel
- Refactor: consolidar a interface operacional e o formato da evidencia sem
  alterar o comportamento padrao do fallback fora da revalidacao estrita

## Criterios de Aceitacao

- Given `ALEMBIC_STRICT_DIRECT_URL=true` e `DIRECT_URL` valida, When
  `alembic upgrade head` ou `alembic current` forem executados para a
  revalidacao do Supabase, Then apenas `DIRECT_URL` e elegivel para a conexao
  e o sucesso da rodada prova que a conexao direta foi a rota usada
- Given `ALEMBIC_STRICT_DIRECT_URL=true`, `DATABASE_URL` definida e
  `DIRECT_URL` ausente ou invalida, When a revalidacao estrita for executada,
  Then o fluxo falha cedo sem fallback silencioso para `DATABASE_URL`
- Given `ALEMBIC_STRICT_DIRECT_URL` ausente, When o fluxo Alembic padrao rodar,
  Then o contrato de prioridade e fallback entregue em `ISSUE-F1-01-003`
  permanece inalterado
- Given a nova rodada concluida com sucesso, When a issue for encerrada, Then a
  evidencia minima inclui os comandos executados, o flag de modo estrito, a
  saida observada de `alembic upgrade head`, a saida observada de
  `alembic current`, o resultado de `alembic heads`, o resultado do teste de
  head unico e a declaracao explicita de prontidao ou bloqueio para F2
- Given a evidencia da rodada, When um revisor ler o artefato sem memoria da
  sessao, Then ele consegue verificar que a revalidacao nao dependeu de
  inferencia sobre o uso de `DIRECT_URL`

## Definition of Done da Issue

- [x] modo estrito `ALEMBIC_STRICT_DIRECT_URL=true` implementado no fluxo
      Alembic sem quebrar o comportamento padrao
- [x] cobertura automatizada protege o modo estrito e preserva o fallback
      padrao fora dele
- [x] rodada real de revalidacao no Supabase reexecutada com o modo estrito
- [x] evidencia nova consolidada com saidas observadas e segredos mascarados
- [x] status de prontidao da F2 declarado com base na nova evidencia

## Tasks Decupadas

- [x] T1: delimitar o contrato do modo estrito de revalidacao do Supabase
- [x] T2: implementar o modo estrito sem quebrar o fallback padrao do Alembic
- [x] T3: adicionar cobertura de regressao para o modo estrito e o modo padrao
- [x] T4: rerodar a revalidacao real e consolidar a evidencia rastreavel

## Instructions por Task

### T1
- objetivo: fixar o contrato exato da revalidacao estrita sem reabrir o escopo
  geral de migrations
- precondicoes: `ISSUE-F1-01-003` e `ISSUE-F1-01-004` lidas; revisao
  pos-issue consolidada; acesso aos arquivos do fluxo Alembic e ao artefato de
  evidencia atual
- arquivos_a_ler_ou_tocar:
  - `backend/alembic/env.py`
  - `backend/scripts/migrate.ps1`
  - `backend/tests/test_alembic_env_contract.py`
  - `PROJETOS/SUPABASE/F1-Schema-no-Supabase/EVIDENCIA-F1-01-004-Revalidacao-Supabase.md`
- passos_atomicos:
  1. confirmar que o comportamento padrao entregue em `ISSUE-F1-01-003`
     continua valido quando nenhum flag de revalidacao estrita estiver ativo
  2. fixar nesta issue que o modo estrito sera ativado exclusivamente por
     `ALEMBIC_STRICT_DIRECT_URL=true`
  3. fixar que, nesse modo, `get_urls()` deve expor somente `DIRECT_URL` e
     falhar cedo se `DIRECT_URL` nao estiver disponivel, mesmo que
     `DATABASE_URL` exista
  4. fixar que `backend/scripts/migrate.ps1` deve expor a mesma capacidade via
     parametro ou export explicito do flag, sem mudar o default do wrapper
  5. parar se a correcao exigir alterar o contrato de runtime da aplicacao ou
     o fallback SQLite de testes fora do fluxo Alembic
- comandos_permitidos:
  - `rg -n "DIRECT_URL|DATABASE_URL|get_urls|run_migrations_online|STRICT" backend/alembic/env.py backend/scripts/migrate.ps1 backend/tests`
- resultado_esperado: fronteira clara entre o fluxo Alembic padrao e a
  revalidacao estrita do Supabase
- testes_ou_validacoes_obrigatorias:
  - confirmar por leitura que a issue nao altera o contrato de runtime em
    `backend/app/db/database.py`
- stop_conditions:
  - parar se a solucao exigir mudar o comportamento padrao de runtime ou mover
    o problema para F2/F3

### T2
- objetivo: implementar o modo estrito de revalidacao do Supabase com impacto
  local e controlado
- precondicoes: T1 concluida; interface `ALEMBIC_STRICT_DIRECT_URL=true`
  definida
- arquivos_a_ler_ou_tocar:
  - `backend/alembic/env.py`
  - `backend/scripts/migrate.ps1`
- passos_atomicos:
  1. ajustar `backend/alembic/env.py` para ler `ALEMBIC_STRICT_DIRECT_URL`
  2. quando o flag estiver ativo, retornar somente `DIRECT_URL` em `get_urls()`
     e emitir erro objetivo se `DIRECT_URL` estiver ausente ou vazia
  3. preservar exatamente o comportamento padrao atual quando o flag nao estiver
     ativo, incluindo a ordem `DIRECT_URL` -> `DATABASE_URL`
  4. atualizar `backend/scripts/migrate.ps1` para permitir o uso do modo
     estrito de forma explicita, sem alterar o comportamento default do script
  5. nao introduzir fallback alternativo, heuristica por hostname ou qualquer
     decisao automatica baseada em "Supabase"
- comandos_permitidos:
  - `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python3 -m pytest -q tests/test_alembic_env_contract.py`
- resultado_esperado: revalidacao estrita consegue provar uso de
  `DIRECT_URL` por construcao, sem quebrar o fluxo padrao
- testes_ou_validacoes_obrigatorias:
  - validar que o modo estrito falha sem `DIRECT_URL`
  - validar que o modo padrao continua aceitando o contrato anterior
- stop_conditions:
  - parar se a implementacao mascarar erro real de migration ou alterar o
    comportamento padrao quando o flag estiver ausente

### T3
- objetivo: cobrir por regressao automatizada o modo estrito e a compatibilidade
  com o modo padrao
- precondicoes: T2 concluida; fluxo final estabilizado
- arquivos_a_ler_ou_tocar:
  - `backend/tests/test_alembic_env_contract.py`
  - `backend/tests/test_alembic_single_head.py`
  - `backend/alembic/env.py`
- passos_atomicos:
  1. adicionar teste que prove que `ALEMBIC_STRICT_DIRECT_URL=true` expone
     apenas `DIRECT_URL`, ignorando `DATABASE_URL`
  2. adicionar teste que prove que o modo estrito falha cedo quando
     `DIRECT_URL` nao estiver configurada, mesmo com `DATABASE_URL` presente
  3. manter ou ajustar os testes existentes para provar que o modo padrao
     continua igual ao comportamento entregue em `ISSUE-F1-01-003`
  4. reexecutar o teste de head unico para garantir que a correcao nao mexeu no
     historico Alembic
- comandos_permitidos:
  - `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python3 -m pytest -q tests/test_alembic_env_contract.py tests/test_alembic_single_head.py`
- resultado_esperado: cobertura local suficiente para sustentar a correcao sem
  depender de um banco Supabase real
- testes_ou_validacoes_obrigatorias:
  - `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python3 -m pytest -q tests/test_alembic_env_contract.py tests/test_alembic_single_head.py`
- stop_conditions:
  - parar se os testes exigirem credenciais reais do Supabase ou operacao
    destrutiva fora do escopo da issue

### T4
- objetivo: rerodar a validacao real com modo estrito e produzir evidencia
  objetiva suficiente para auditoria posterior
- precondicoes: T3 concluida; `DIRECT_URL` valida para o ambiente alvo;
  credenciais disponiveis de forma controlada
- arquivos_a_ler_ou_tocar:
  - `backend/alembic/env.py`
  - `backend/scripts/migrate.ps1`
  - `PROJETOS/SUPABASE/F1-Schema-no-Supabase/EVIDENCIA-F1-01-005-Revalidacao-Sem-Fallback-Ambiguo.md`
  - `PROJETOS/SUPABASE/F1-Schema-no-Supabase/EVIDENCIA-F1-01-004-Revalidacao-Supabase.md`
- passos_atomicos:
  1. executar a rodada real contra o Supabase com
     `ALEMBIC_STRICT_DIRECT_URL=true` para `alembic upgrade head`
  2. executar `alembic current` com o mesmo modo estrito
  3. reexecutar `alembic heads` e `pytest -q tests/test_alembic_single_head.py`
  4. registrar em
     `EVIDENCIA-F1-01-005-Revalidacao-Sem-Fallback-Ambiguo.md`
     os comandos usados, o flag de modo estrito, a saida observada dos
     comandos, a revision final observada e a declaracao explicita de liberacao
     ou bloqueio da F2
  5. mascarar segredos e URLs sensiveis na evidencia, preservando a parte da
     saida necessaria para auditoria
  6. manter `EVIDENCIA-F1-01-004-Revalidacao-Supabase.md` apenas como trilha
     historica; a prontidao final para F2 deve passar a depender da nova
     evidencia desta issue
- comandos_permitidos:
  - `cd backend && ALEMBIC_STRICT_DIRECT_URL=true DIRECT_URL="$DIRECT_URL" DATABASE_URL="$DATABASE_URL" alembic upgrade head`
  - `cd backend && ALEMBIC_STRICT_DIRECT_URL=true DIRECT_URL="$DIRECT_URL" DATABASE_URL="$DATABASE_URL" alembic current`
  - `cd backend && TESTING=true python3 -m alembic heads`
  - `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python3 -m pytest -q tests/test_alembic_single_head.py`
- resultado_esperado: evidencia rastreavel suficiente para provar que a rodada
  real usou somente `DIRECT_URL` no caminho de validacao do Supabase
- testes_ou_validacoes_obrigatorias:
  - confirmar que a nova evidencia inclui a saida observada de
    `alembic upgrade head`
  - confirmar que a nova evidencia inclui a saida observada de
    `alembic current`
  - confirmar que a nova evidencia inclui `a7b8c9d0e1f2 (head)` ou o head que
    estiver vigente no repositorio no momento da rodada
  - confirmar que a nova evidencia inclui o resultado do teste de head unico
- stop_conditions:
  - parar se a rodada real falhar, se a revision final nao puder ser determinada
    com seguranca ou se a evidencia final continuar dependente de inferencia

## Arquivos Reais Envolvidos

- `backend/alembic/env.py`
- `backend/scripts/migrate.ps1`
- `backend/tests/test_alembic_env_contract.py`
- `backend/tests/test_alembic_single_head.py`
- `PROJETOS/SUPABASE/F1-Schema-no-Supabase/EVIDENCIA-F1-01-004-Revalidacao-Supabase.md`
- `PROJETOS/SUPABASE/F1-Schema-no-Supabase/EVIDENCIA-F1-01-005-Revalidacao-Sem-Fallback-Ambiguo.md`

## Artifact Minimo

- modo estrito `ALEMBIC_STRICT_DIRECT_URL=true` implementado e coberto por teste
- `PROJETOS/SUPABASE/F1-Schema-no-Supabase/EVIDENCIA-F1-01-005-Revalidacao-Sem-Fallback-Ambiguo.md`
  com comandos executados, saidas observadas mascaradas, revision final e
  declaracao explicita da prontidao da F2

## Dependencias

- [Intake](../../INTAKE-SUPABASE.md)
- [Epic](../EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md)
- [Fase](../F1_SUPABASE_EPICS.md)
- [PRD](../../PRD-SUPABASE.md)
- [ISSUE-F1-01-004](./ISSUE-F1-01-004-Revalidar-Upgrade-Head-no-Supabase-com-Evidencia-Rastreavel.md)
- [ISSUE-F1-01-003](./ISSUE-F1-01-003-Endurecer-Fallback-de-URLs-no-Fluxo-Alembic.md)
