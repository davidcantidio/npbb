---
doc_id: "ISSUE-F2-01-001-Formalizar-Runbook-de-Backup-Export-Import-e-Rollback.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-16"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-01-001 - Formalizar runbook de backup, export, import e rollback

## User Story

Como operador responsavel pela migracao, quero um runbook unificado de backup,
export, import e rollback, para executar a troca de dados no Supabase sem
improvisar passos criticos.

## Contexto Tecnico

O PRD ja definiu os limites desta fase: schema primeiro, backup previo do
Supabase, export do PostgreSQL local com `pg_dump` ou formato equivalente,
import com `psql` ou `pg_restore`, e ordem segura de execucao. Esta issue fecha
os detalhes operacionais que o PRD reservou para F2, sem inventar requisitos
fora desse escopo.

## Plano TDD
- Red: expor lacunas operacionais que impediriam uma rodada segura de migracao
- Green: transformar as diretrizes do PRD em uma sequencia executavel e verificavel
- Refactor: remover ambiguidades entre setup, troubleshooting e fluxo de migracao

## Criterios de Aceitacao
- Given F1 concluida, When o runbook estiver formalizado, Then ele define precondicoes, backup, export, import, validacao e rollback em ordem explicita
- Given a existencia de FKs e dados antigos no Supabase, When o runbook descreve a recarga, Then a limpeza e a importacao seguem uma sequencia segura
- Given necessidade de rollback, When o operador consultar o runbook, Then o caminho de retorno ao backup do Supabase esta descrito de forma objetiva

## Definition of Done da Issue
- [x] runbook unico fechado para backup, export, import, validacao e rollback
- [x] sequencia operacional alinhada ao PRD e aos contratos atuais de conexao
- [x] criterios de parada e precondicoes criticas declarados

## Tasks Decupadas
- [x] T1: consolidar as restricoes e precondicoes do PRD e do repositorio para a migracao de dados
- [x] T2: definir a sequencia canonica de backup, export, import, validacao e rollback
- [x] T3: validar o runbook contra os contratos atuais de conexao, tooling e risco operacional

## Instructions por Task

### T1
- objetivo: reunir apenas os fatos necessarios para a rodada de migracao de dados sem extrapolar o PRD
- precondicoes: F1 concluida; PRD e intake lidos; acesso aos arquivos operacionais do repositorio
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/SUPABASE/PRD-SUPABASE.md`
  - `PROJETOS/SUPABASE/INTAKE-SUPABASE.md`
  - `backend/.env.example`
  - `docs/SETUP.md`
  - `docs/TROUBLESHOOTING.md`
- passos_atomicos:
  1. extrair do PRD a ordem obrigatoria: schema primeiro, backup do Supabase, export do local, recarga, validacao e rollback
  2. revisar em `backend/.env.example` e `docs/SETUP.md` como `DATABASE_URL` e `DIRECT_URL` estao descritas hoje
  3. revisar em `docs/TROUBLESHOOTING.md` os riscos operacionais ja conhecidos para Supabase e Alembic
  4. listar as precondicoes objetivas da rodada, incluindo credenciais, acesso ao banco local e ferramenta de dump/import
- comandos_permitidos:
  - `rg -n "DATABASE_URL|DIRECT_URL|pg_dump|pg_restore|Supabase|5432|6543" PROJETOS/SUPABASE/PRD-SUPABASE.md backend/.env.example docs/SETUP.md docs/TROUBLESHOOTING.md`
- resultado_esperado: conjunto minimo de restricoes e precondicoes da migracao de dados consolidado
- testes_ou_validacoes_obrigatorias:
  - confirmar que nenhuma precondicao adicionada contradiz o PRD
- stop_conditions:
  - parar se faltar insumo essencial para descrever precondicoes de backup ou export

### T2
- objetivo: transformar as restricoes da migracao em uma sequencia operacional unica e executavel
- precondicoes: T1 concluida; ordem macro do PRD consolidada
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/SUPABASE/PRD-SUPABASE.md`
  - `backend/.env.example`
  - `backend/scripts/seed_common.py`
  - `docs/SETUP.md`
- passos_atomicos:
  1. definir a ordem canonica da rodada: backup do Supabase, export do PostgreSQL local, limpeza controlada do alvo, import, validacao e rollback
  2. registrar quais comandos-base da rodada usam `pg_dump`, `psql` ou `pg_restore`, mantendo apenas as alternativas previstas no PRD
  3. explicitar onde `DIRECT_URL` e obrigatoria e onde `DATABASE_URL` pode permanecer como referencia de runtime
  4. declarar os criterios de parada antes de qualquer passo destrutivo
- comandos_permitidos:
  - `rg -n "DIRECT_URL|DATABASE_URL" backend/.env.example backend/scripts/seed_common.py`
- resultado_esperado: runbook com ordem objetiva, comandos-base e criterios de parada claros
- testes_ou_validacoes_obrigatorias:
  - verificar que a sequencia inclui backup antes de qualquer limpeza do Supabase
- stop_conditions:
  - parar se a ordem segura de limpeza/import depender de informacao ainda nao recuperada sobre o schema atual

### T3
- objetivo: validar que o runbook e operacionalmente coerente com o ambiente atual do repositorio
- precondicoes: T2 concluida; sequencia canonica fechada
- arquivos_a_ler_ou_tocar:
  - `backend/.env.example`
  - `docs/SETUP.md`
  - `docs/TROUBLESHOOTING.md`
  - `docs/DEPLOY_RENDER_CLOUDFLARE.md`
- passos_atomicos:
  1. conferir se o runbook nao contradiz a separacao entre `DATABASE_URL` de runtime e `DIRECT_URL` de operacoes sensiveis
  2. conferir se a rodada de dados nao introduz qualquer dependencia de frontend ou Supabase Auth
  3. validar que o rollback descrito preserva o backup do Supabase ate o fim da validacao da F3
  4. liberar o runbook somente se todos os passos e stop conditions estiverem verificaveis
- comandos_permitidos:
  - `rg -n "Supabase|DATABASE_URL|DIRECT_URL|go-live|Render" docs/SETUP.md docs/TROUBLESHOOTING.md docs/DEPLOY_RENDER_CLOUDFLARE.md`
- resultado_esperado: runbook coerente com o ambiente atual e pronto para orientar a automacao da issue seguinte
- testes_ou_validacoes_obrigatorias:
  - confirmar que o runbook nao cria requisito novo fora do PRD
- stop_conditions:
  - parar se surgir dependencia nao documentada de infraestrutura que mude a ordem da migracao

## Arquivos Reais Envolvidos
- `PROJETOS/SUPABASE/PRD-SUPABASE.md`
- `PROJETOS/SUPABASE/INTAKE-SUPABASE.md`
- `backend/.env.example`
- `backend/scripts/seed_common.py`
- `docs/SETUP.md`
- `docs/TROUBLESHOOTING.md`
- `docs/DEPLOY_RENDER_CLOUDFLARE.md`

## Artifact Minimo

Runbook unico com precondicoes, sequencia operacional, validacoes e rollback da
migracao de dados.

**Artifact gerado:** [docs/RUNBOOK-MIGRACAO-SUPABASE.md](../../../../docs/RUNBOOK-MIGRACAO-SUPABASE.md)

## Dependencias
- [Intake](../../INTAKE-SUPABASE.md)
- [Epic](../EPIC-F2-01-Preparar-Backup-e-Export-do-PostgreSQL-Local.md)
- [Fase](../F2_SUPABASE_EPICS.md)
- [PRD](../../PRD-SUPABASE.md)
- [F1](../../F1-Schema-no-Supabase/F1_SUPABASE_EPICS.md)
