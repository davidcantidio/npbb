---
doc_id: "ISSUE-F3-01-002-Validar-Scripts-Criticos-e-Invariantes-de-Teste.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-16"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F3-01-002 - Validar scripts criticos e invariantes de teste

## User Story

Como mantenedor do backend, quero validar os scripts criticos e o fallback de
testes apos o cutover do banco, para manter coerencia entre operacao em
Supabase e testes isolados em SQLite.

## Contexto Tecnico

`backend/scripts/seed_common.py` concentra a preferencia por `DIRECT_URL` para
scripts sensiveis de banco. Ao mesmo tempo, `backend/app/db/database.py` deve
manter o fallback SQLite quando `TESTING=true`. Esta issue garante que essas
duas frentes continuam coerentes apos a migracao do banco.

## Plano TDD
- Red: falhar se scripts sensiveis apontarem para um contrato de URL incoerente ou se o fallback SQLite regredir
- Green: validar os scripts criticos contra o contrato atual e confirmar o fallback de testes
- Refactor: consolidar um checklist minimo de manutencao para o estado pos-cutover

## Criterios de Aceitacao
- Given scripts criticos do backend, When o contrato de conexao for revisado, Then eles permanecem coerentes com `DIRECT_URL` e `DATABASE_URL`
- Given `TESTING=true`, When o backend resolve a URL de banco para testes, Then o fallback continua em SQLite
- Given a revisao encerrada, When a fase final for documentada, Then existe evidencia minima de que operacao e testes continuam coerentes

## Definition of Done da Issue
- [ ] scripts criticos revisados contra o contrato atual de conexao
- [ ] fallback SQLite de testes confirmado
- [ ] evidencias minimas de manutencao consolidadas

## Tasks Decupadas
- [ ] T1: revisar scripts criticos contra o contrato atual de conexao
- [ ] T2: validar explicitamente o fallback SQLite quando `TESTING=true`
- [ ] T3: consolidar as evidencias minimas para a fase documental

## Instructions por Task

### T1
- objetivo: confirmar que os scripts criticos do backend continuam usando o contrato de conexao correto apos o cutover
- precondicoes: ISSUE-F3-01-001 concluida ou sem bloqueios de runtime
- arquivos_a_ler_ou_tocar:
  - `backend/scripts/seed_common.py`
  - `backend/scripts/seed_domains.py`
  - `backend/scripts/seed_sample.py`
  - `backend/.env.example`
- passos_atomicos:
  1. revisar em `seed_common.py` a preferencia por `DIRECT_URL` para operacoes sensiveis
  2. revisar em `seed_domains.py` e `seed_sample.py` como esses scripts consomem o helper comum ou as variaveis de ambiente
  3. confirmar que nenhum deles assume PostgreSQL local como requisito padrao
  4. registrar qualquer divergencia objetiva antes da etapa documental
- comandos_permitidos:
  - `rg -n "DIRECT_URL|DATABASE_URL|sqlite" backend/scripts/seed_common.py backend/scripts/seed_domains.py backend/scripts/seed_sample.py backend/.env.example`
- resultado_esperado: scripts criticos coerentes com o contrato atual de conexao
- testes_ou_validacoes_obrigatorias:
  - confirmar que scripts sensiveis preferem `DIRECT_URL` quando apropriado
- stop_conditions:
  - parar se algum script critico ainda assumir banco local como fluxo principal

### T2
- objetivo: provar explicitamente que o backend preserva o fallback de testes em SQLite
- precondicoes: T1 concluida
- arquivos_a_ler_ou_tocar:
  - `backend/app/db/database.py`
  - `backend/tests/test_alembic_single_head.py`
- passos_atomicos:
  1. revisar a funcao de resolucao de URL em `backend/app/db/database.py`
  2. executar uma validacao direta da resolucao com `TESTING=true`
  3. executar a validacao automatizada minima existente do historico Alembic em contexto de testes
  4. registrar o resultado como evidencia de que a migracao para Supabase nao removeu o isolamento dos testes
- comandos_permitidos:
  - `cd backend && PYTHONPATH=.. TESTING=true python -c "from app.db.database import _get_database_url; print(_get_database_url())"`
  - `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python -m pytest -q tests/test_alembic_single_head.py`
- resultado_esperado: fallback de testes resolvido para SQLite e validacao minima verde
- testes_ou_validacoes_obrigatorias:
  - `cd backend && PYTHONPATH=.. TESTING=true python -c "from app.db.database import _get_database_url; print(_get_database_url())"`
  - `cd backend && PYTHONPATH=.. TESTING=true SECRET_KEY=ci-secret-key python -m pytest -q tests/test_alembic_single_head.py`
- stop_conditions:
  - parar se o fallback de testes deixar de apontar para SQLite ou se a validacao minima falhar

### T3
- objetivo: consolidar as evidencias minimas de scripts e testes para a fase documental final
- precondicoes: T2 concluida
- arquivos_a_ler_ou_tocar:
  - `backend/scripts/seed_common.py`
  - `backend/app/db/database.py`
  - `docs/TROUBLESHOOTING.md`
- passos_atomicos:
  1. resumir o estado dos scripts criticos e do fallback SQLite
  2. registrar os bloqueios objetivos restantes, se existirem
  3. sinalizar quais pontos precisam aparecer na issue documental final
  4. liberar a issue somente se operacao e testes estiverem coerentes com o novo banco unico
- comandos_permitidos:
  - `rg -n "DIRECT_URL|DATABASE_URL|sqlite|TESTING" backend/scripts/seed_common.py backend/app/db/database.py docs/TROUBLESHOOTING.md`
- resultado_esperado: evidencias minimas consolidadas para orientar a documentacao final do projeto
- testes_ou_validacoes_obrigatorias:
  - confirmar que nao ha contradicao entre scripts de operacao e fallback de testes
- stop_conditions:
  - parar se a fase documental nao puder afirmar com seguranca o estado final de operacao e testes

## Arquivos Reais Envolvidos
- `backend/scripts/seed_common.py`
- `backend/scripts/seed_domains.py`
- `backend/scripts/seed_sample.py`
- `backend/app/db/database.py`
- `backend/tests/test_alembic_single_head.py`
- `backend/.env.example`
- `docs/TROUBLESHOOTING.md`

## Artifact Minimo

Checklist minimo comprovando coerencia entre scripts criticos, Supabase em
operacao e SQLite em testes.

## Dependencias
- [Intake](../../INTAKE-SUPABASE.md)
- [Epic](../EPIC-F3-01-Validar-Backend-e-Scripts-Criticos-contra-Supabase.md)
- [Fase](../F3_SUPABASE_EPICS.md)
- [PRD](../../PRD-SUPABASE.md)
- [ISSUE-F3-01-001](./ISSUE-F3-01-001-Validar-Runtime-do-Backend-com-Supabase.md)
