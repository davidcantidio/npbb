---
doc_id: "ISSUE-F1-01-006-Fechar-Cobertura-do-Modo-Estrito-e-Alinhar-Gate-da-Fase.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-16"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-01-006 - Fechar cobertura do modo estrito e alinhar gate da fase

## User Story

Como revisor da F1, quero fechar a lacuna de regressao do modo estrito do Alembic
e alinhar o estado documental do gate da fase para que a liberacao da F2 e a
trilha de auditoria permaneçam verificaveis sem ambiguidade.

## Contexto Tecnico

Esta issue nasce da revisao pos-issue de `ISSUE-F1-01-005`.

Rastreabilidade obrigatoria desta issue:
- issue de origem: `ISSUE-F1-01-005`
- evidencia usada na revisao: `BASE_COMMIT=worktree`, `git status --short`,
  leitura de
  `backend/alembic/env.py`,
  `backend/tests/test_alembic_env_contract.py`,
  `backend/tests/test_alembic_single_head.py`,
  `PROJETOS/SUPABASE/F1-Schema-no-Supabase/EVIDENCIA-F1-01-005-Revalidacao-Sem-Fallback-Ambiguo.md`,
  `PROJETOS/SUPABASE/F1-Schema-no-Supabase/F1_SUPABASE_EPICS.md`,
  alem da reexecucao de
  `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python3 -m pytest -q tests/test_alembic_env_contract.py tests/test_alembic_single_head.py`
  e
  `cd backend && TESTING=true python3 -m alembic heads`
- sintoma observado: a `ISSUE-F1-01-005` implementou o modo estrito e produziu
  evidencia operacional, mas a cobertura automatizada nao protege explicitamente
  o caso de `DIRECT_URL` invalida com `ALEMBIC_STRICT_DIRECT_URL=true` e
  `DATABASE_URL` presente; adicionalmente, o manifesto da fase ficou com
  `audit_gate: pending` no frontmatter e `gate_atual: not_ready` no corpo
- risco de nao corrigir: alteracoes futuras podem reintroduzir fallback ou
  comportamento ambiguo no modo estrito sem falha imediata da suite; a trilha
  documental da F1 permanece inconsistente para auditoria e planejamento da F2

Escopo desta correcao:
- adicionar cobertura de regressao para o caso de `DIRECT_URL` invalida no modo
  estrito, sem alterar o contrato ja entregue do fluxo padrao
- manter o comportamento do modo estrito como exclusivo de `DIRECT_URL`
- alinhar o manifesto da fase para que o estado do gate de auditoria seja
  consistente entre frontmatter e corpo
- nao reexecutar a rodada real no Supabase nem alterar o veredito funcional da
  `ISSUE-F1-01-005`

## Plano TDD

- Red: adicionar teste que demonstre que uma `DIRECT_URL` invalida em modo
  estrito falha sem fallback para `DATABASE_URL`
- Green: ajustar o contrato testado, se necessario, para que o modo estrito
  continue tentando somente `DIRECT_URL` e devolva erro claro
- Refactor: alinhar a documentacao da fase sem mexer no escopo do epico ou da F2

## Criterios de Aceitacao

- Given `ALEMBIC_STRICT_DIRECT_URL=true`, `DIRECT_URL` invalida e
  `DATABASE_URL` valida, When `run_migrations_online()` for exercitado, Then o
  fluxo tenta apenas `DIRECT_URL` e falha sem fallback para `DATABASE_URL`
- Given o modo estrito ja implementado, When a suite local de regressao for
  executada, Then ela cobre os casos de `DIRECT_URL` valida, ausente e invalida
  sem depender de credenciais reais do Supabase
- Given a fase F1 esta com todos os epicos `done` e aguardando auditoria, When
  o manifesto da fase for lido, Then o estado do gate de auditoria aparece de
  forma consistente no frontmatter e no corpo
- Given a issue for concluida, When um revisor ler apenas os artefatos
  atualizados, Then ele consegue verificar que a lacuna de regressao foi fechada
  e que a fase nao apresenta ambiguidade documental sobre o gate atual

## Definition of Done da Issue

- [x] teste de regressao para `DIRECT_URL` invalida em modo estrito adicionado
      e passando
- [x] suite local relacionada executada com sucesso
- [x] manifesto da fase F1 alinhado entre frontmatter e secao de estado do gate
- [x] issue de origem e evidencias desta revisao permanecem rastreaveis nesta
      issue
- [x] nenhum comportamento funcional do fluxo padrao fora do modo estrito foi
      alterado

## Tasks Decupadas

- [x] T1: fechar a cobertura de regressao do modo estrito para `DIRECT_URL` invalida
- [x] T2: alinhar o estado documental do gate da fase F1
- [x] T3: revalidar a suite local e consolidar o fechamento da issue

## Instructions por Task

### T1
- objetivo: proteger por regressao o ramo estrito quando `DIRECT_URL` estiver
  configurada mas invalida
- precondicoes: `ISSUE-F1-01-005` lida; contrato do modo estrito entendido;
  ambiente de testes backend funcional
- arquivos_a_ler_ou_tocar:
  - `backend/alembic/env.py`
  - `backend/tests/test_alembic_env_contract.py`
- passos_atomicos:
  1. localizar os testes existentes do modo padrao e do modo estrito
  2. adicionar um teste especifico para `ALEMBIC_STRICT_DIRECT_URL=true` com
     `DIRECT_URL` invalida e `DATABASE_URL` presente
  3. provar no teste que apenas `DIRECT_URL` foi tentada e que nao houve
     fallback para `DATABASE_URL`
  4. ajustar mensagens ou comportamento apenas se o teste revelar ambiguidade
     real no contrato
  5. preservar intacto o comportamento do modo padrao entregue em
     `ISSUE-F1-01-003` e `ISSUE-F1-01-005`
- comandos_permitidos:
  - `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python3 -m pytest -q tests/test_alembic_env_contract.py`
- resultado_esperado: a suite cobre explicitamente o caso de `DIRECT_URL`
  invalida em modo estrito sem fallback para `DATABASE_URL`
- testes_ou_validacoes_obrigatorias:
  - `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python3 -m pytest -q tests/test_alembic_env_contract.py`
- stop_conditions:
  - parar se a correcao exigir mudar o contrato funcional do modo padrao ou
    introduzir dependencia de banco real

### T2
- objetivo: remover a ambiguidade documental do gate atual da fase F1
- precondicoes: status dos epicos e issues da F1 confirmado como concluido;
  entendimento das regras de gate em `GOV-SCRUM.md` e `GOV-ISSUE-FIRST.md`
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/SUPABASE/F1-Schema-no-Supabase/F1_SUPABASE_EPICS.md`
  - `PROJETOS/SUPABASE/F1-Schema-no-Supabase/EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md`
- passos_atomicos:
  1. confirmar qual estado do gate esta vigente documentalmente para a fase
  2. alinhar a secao `Estado do Gate de Auditoria` ao mesmo estado do
     frontmatter
  3. nao alterar o status do epico, nao reabrir issues e nao simular auditoria
  4. manter a correcao limitada ao manifesto da fase
- comandos_permitidos:
  - `sed -n '1,220p' PROJETOS/SUPABASE/F1-Schema-no-Supabase/F1_SUPABASE_EPICS.md`
- resultado_esperado: manifesto da fase sem contradicao entre frontmatter e
  corpo sobre o gate atual
- testes_ou_validacoes_obrigatorias:
  - confirmar por leitura que o manifesto da fase ficou coerente
- stop_conditions:
  - parar se a correcao exigir alterar o resultado de auditoria inexistente ou
    reabrir a fase fora das regras do framework

### T3
- objetivo: revalidar o escopo local corrigido e fechar a issue com evidencia suficiente
- precondicoes: T1 e T2 concluidas
- arquivos_a_ler_ou_tocar:
  - `backend/tests/test_alembic_env_contract.py`
  - `backend/tests/test_alembic_single_head.py`
  - `PROJETOS/SUPABASE/F1-Schema-no-Supabase/F1_SUPABASE_EPICS.md`
- passos_atomicos:
  1. executar a suite local relacionada ao contrato Alembic
  2. reexecutar a verificacao de head unico
  3. confirmar por leitura a coerencia final do manifesto da fase
  4. atualizar o status desta issue e o DoD apenas se todas as validacoes
     obrigatorias tiverem passado
- comandos_permitidos:
  - `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python3 -m pytest -q tests/test_alembic_env_contract.py tests/test_alembic_single_head.py`
  - `cd backend && TESTING=true python3 -m alembic heads`
- resultado_esperado: regressao fechada, historico Alembic preservado e
  manifesto da fase coerente
- testes_ou_validacoes_obrigatorias:
  - `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python3 -m pytest -q tests/test_alembic_env_contract.py tests/test_alembic_single_head.py`
  - `cd backend && TESTING=true python3 -m alembic heads`
- stop_conditions:
  - parar se a suite revelar regressao funcional alem do escopo local ou se o
    head Alembic deixar de ser unico

## Arquivos Reais Envolvidos

- `backend/alembic/env.py`
- `backend/tests/test_alembic_env_contract.py`
- `backend/tests/test_alembic_single_head.py`
- `PROJETOS/SUPABASE/F1-Schema-no-Supabase/F1_SUPABASE_EPICS.md`
- `PROJETOS/SUPABASE/F1-Schema-no-Supabase/issues/ISSUE-F1-01-005-Endurecer-Revalidacao-Head-no-Supabase-sem-Fallback-Ambiguo.md`
- `PROJETOS/SUPABASE/F1-Schema-no-Supabase/EVIDENCIA-F1-01-005-Revalidacao-Sem-Fallback-Ambiguo.md`

## Artifact Minimo

- teste de regressao cobrindo `DIRECT_URL` invalida em modo estrito
- suite local relacionada executada com sucesso
- manifesto da fase F1 coerente sobre o estado do gate de auditoria

## Dependencias

- [Intake](../../INTAKE-SUPABASE.md)
- [Epic](../EPIC-F1-01-Compatibilizar-e-Validar-Migrations-Alembic-no-Supabase.md)
- [Fase](../F1_SUPABASE_EPICS.md)
- [PRD](../../PRD-SUPABASE.md)
- [ISSUE-F1-01-005](./ISSUE-F1-01-005-Endurecer-Revalidacao-Head-no-Supabase-sem-Fallback-Ambiguo.md)
- [ISSUE-F1-01-003](./ISSUE-F1-01-003-Endurecer-Fallback-de-URLs-no-Fluxo-Alembic.md)
