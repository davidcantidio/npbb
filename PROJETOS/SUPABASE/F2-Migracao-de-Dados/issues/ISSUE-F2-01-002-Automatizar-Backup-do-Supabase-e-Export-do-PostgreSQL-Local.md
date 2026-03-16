---
doc_id: "ISSUE-F2-01-002-Automatizar-Backup-do-Supabase-e-Export-do-PostgreSQL-Local.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-16"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-01-002 - Automatizar backup do Supabase e export do PostgreSQL local

## User Story

Como operador da migracao, quero automatizar o backup do Supabase e o export do
PostgreSQL local, para produzir os artefatos da rodada de dados com comandos
reproduziveis e seguros antes de qualquer passo destrutivo.

## Contexto Tecnico

O runbook da issue anterior define a ordem da rodada. Esta issue materializa os
passos nao destrutivos: gerar backup do Supabase antes da substituicao e export
do PostgreSQL local no formato previsto pelo PRD, usando `pg_dump` e o contrato
de conexao vigente no repositorio.

## Plano TDD
- Red: falhar cedo se credenciais, tooling ou parametros minimos nao estiverem disponiveis
- Green: produzir backup e export com comandos reproduziveis e alinhados ao runbook
- Refactor: consolidar mensagens de erro e precondicoes de execucao

## Criterios de Aceitacao
- Given o runbook aprovado e credenciais validas, When a automacao roda, Then o backup do Supabase e gerado antes de qualquer acao de recarga
- Given acesso ao PostgreSQL local, When a automacao roda, Then o export dos dados locais e produzido no formato previsto pelo runbook
- Given falta de credencial ou de `pg_dump`, When a automacao e iniciada, Then o fluxo falha antes de qualquer efeito colateral no Supabase

## Definition of Done da Issue
- [x] automacao gera backup do Supabase de forma reproduzivel
- [x] automacao gera export do PostgreSQL local no formato aprovado
- [x] precondicoes e falhas antecipadas estao declaradas de forma objetiva

## Tasks Decupadas
- [x] T1: fechar a interface operacional da automacao a partir do runbook aprovado
- [x] T2: implementar os passos de backup do Supabase e export do PostgreSQL local
- [x] T3: validar a rodada nao destrutiva e consolidar os artefatos gerados

## Instructions por Task

### T1
- objetivo: transformar o runbook aprovado em uma interface operacional unica para backup e export
- precondicoes: ISSUE-F2-01-001 concluida; acesso aos contratos atuais de conexao
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/SUPABASE/PRD-SUPABASE.md`
  - `backend/.env.example`
  - `backend/scripts/seed_common.py`
  - `docs/SETUP.md`
- passos_atomicos:
  1. revisar no runbook aprovado quais variaveis e comandos-base precisam ser expostos para backup e export
  2. alinhar essa interface ao contrato existente de `DIRECT_URL` e `DATABASE_URL`
  3. definir as precondicoes minimas de execucao, incluindo acesso ao Supabase, acesso ao PostgreSQL local e disponibilidade do `pg_dump`
  4. garantir que a interface desta automacao nao inclua nenhum passo destrutivo no Supabase
- comandos_permitidos:
  - `rg -n "DATABASE_URL|DIRECT_URL|pg_dump" backend/.env.example backend/scripts/seed_common.py docs/SETUP.md`
- resultado_esperado: interface da automacao fechada com inputs minimos e sem ambiguidade
- testes_ou_validacoes_obrigatorias:
  - confirmar que a automacao cobre backup do Supabase e export do local, e nada alem disso
- stop_conditions:
  - parar se a interface exigir credenciais ou arquivos que nao estejam previstos no runbook

### T2
- objetivo: materializar os passos nao destrutivos da rodada de dados com comandos reproduziveis
- precondicoes: T1 concluida; tooling necessario disponivel
- arquivos_a_ler_ou_tocar:
  - `backend/.env.example`
  - `docs/SETUP.md`
  - `docs/TROUBLESHOOTING.md`
  - `backend/scripts/seed_common.py`
- passos_atomicos:
  1. implementar o passo de backup do Supabase antes de qualquer operacao de recarga
  2. implementar o passo de export do PostgreSQL local no formato aprovado pelo runbook
  3. validar que ambos os passos usam as conexoes corretas e emitem falha imediata quando faltar credencial ou ferramenta
  4. preservar o resultado bruto de cada comando para suportar a issue de recarga
- comandos_permitidos:
  - `pg_dump --help`
  - `pg_restore --help`
- resultado_esperado: backup do Supabase e export do PostgreSQL local gerados de forma reproduzivel
- testes_ou_validacoes_obrigatorias:
  - confirmar que nenhum passo desta automacao limpa ou altera dados no Supabase
- stop_conditions:
  - parar se `pg_dump` nao estiver disponivel ou se as credenciais nao permitirem acesso consistente ao banco alvo

### T3
- objetivo: validar a rodada nao destrutiva e preparar os artefatos para a recarga controlada
- precondicoes: T2 concluida com sucesso
- arquivos_a_ler_ou_tocar:
  - `docs/TROUBLESHOOTING.md`
  - `docs/SETUP.md`
  - `backend/.env.example`
- passos_atomicos:
  1. conferir se o backup do Supabase foi produzido antes do export local
  2. conferir se o export local resultou em artefato utilizavel pela issue de recarga
  3. registrar os bloqueios objetivos encontrados, se houver, sem iniciar qualquer limpeza no Supabase
  4. liberar a issue somente com os dois artefatos disponiveis para F2-02
- comandos_permitidos:
  - `pg_restore --list <arquivo_de_backup>`
- resultado_esperado: artefatos de backup e export prontos para alimentar a recarga controlada
- testes_ou_validacoes_obrigatorias:
  - confirmar que o backup pode ser inspecionado e que o export local existe no formato esperado
- stop_conditions:
  - parar se o backup nao for legivel ou se o export local nao puder alimentar o passo de import

## Arquivos Reais Envolvidos
- `backend/.env.example`
- `backend/scripts/seed_common.py`
- `docs/SETUP.md`
- `docs/TROUBLESHOOTING.md`
- `PROJETOS/SUPABASE/PRD-SUPABASE.md`

## Artifact Minimo

Automacao reexecutavel que gera backup do Supabase e export do PostgreSQL local
antes da recarga de dados.

**Artifact gerado:** [backend/scripts/backup_export_migracao.py](../../../../backend/scripts/backup_export_migracao.py) — artefatos em `artifacts_migracao/`.

## Dependencias
- [Intake](../../INTAKE-SUPABASE.md)
- [Epic](../EPIC-F2-01-Preparar-Backup-e-Export-do-PostgreSQL-Local.md)
- [Fase](../F2_SUPABASE_EPICS.md)
- [PRD](../../PRD-SUPABASE.md)
- [ISSUE-F2-01-001](./ISSUE-F2-01-001-Formalizar-Runbook-de-Backup-Export-Import-e-Rollback.md)
