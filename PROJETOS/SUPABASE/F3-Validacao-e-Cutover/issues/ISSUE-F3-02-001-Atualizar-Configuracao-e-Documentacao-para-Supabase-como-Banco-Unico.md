---
doc_id: "ISSUE-F3-02-001-Atualizar-Configuracao-e-Documentacao-para-Supabase-como-Banco-Unico.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-16"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F3-02-001 - Atualizar configuracao e documentacao para Supabase como banco unico

## User Story

Como operador e mantenedor do projeto, quero atualizar a configuracao e a
documentacao para o Supabase como banco unico, para remover o PostgreSQL local
como requisito operacional padrao sem afetar o fallback de testes.

## Contexto Tecnico

O repositorio ainda documenta fortemente o PostgreSQL local em `docs/SETUP.md`,
mesmo que o backend e os docs de deploy ja contem partes do contrato do
Supabase. Esta issue consolida o estado final apos F1 e F2: `DATABASE_URL` para
runtime, `DIRECT_URL` para migrations e scripts sensiveis, PostgreSQL local fora
do caminho principal e SQLite preservado apenas para testes.

## Plano TDD
- Red: identificar inconsistencias documentais e de configuracao entre setup, troubleshooting e deploy
- Green: alinhar os arquivos de configuracao e documentacao ao estado final do projeto
- Refactor: remover instrucoes redundantes ou contraditorias sobre banco local

## Criterios de Aceitacao
- Given `backend/.env.example`, When o operador consultar as variaveis de banco, Then o papel de `DATABASE_URL` e `DIRECT_URL` fica claro para o estado final
- Given `docs/SETUP.md` e `docs/TROUBLESHOOTING.md`, When o setup for seguido, Then o Supabase aparece como caminho padrao e o PostgreSQL local deixa de ser requisito operacional principal
- Given `docs/DEPLOY_RENDER_CLOUDFLARE.md` e `docs/render.yaml`, When o deploy for revisado, Then o contrato final do banco permanece coerente com o ambiente Render + Supabase

## Definition of Done da Issue
- [ ] `.env.example` alinhado ao estado final do banco unico
- [ ] setup e troubleshooting atualizados para Supabase como caminho principal
- [ ] deploy documentado sem contradicao com o estado final validado em F3

## Tasks Decupadas
- [ ] T1: mapear os pontos de drift documental e de configuracao sobre o banco
- [ ] T2: atualizar configuracao e setup para o Supabase como banco unico
- [ ] T3: alinhar troubleshooting e deploy ao estado final validado
- [ ] T4: executar uma revisao final de consistencia entre os arquivos atualizados

## Instructions por Task

### T1
- objetivo: localizar todas as inconsistencias documentais e de configuracao que ainda tratam o PostgreSQL local como caminho principal
- precondicoes: EPIC-F3-01 concluido ou sem bloqueios objetivos
- arquivos_a_ler_ou_tocar:
  - `backend/.env.example`
  - `docs/SETUP.md`
  - `docs/TROUBLESHOOTING.md`
  - `docs/DEPLOY_RENDER_CLOUDFLARE.md`
  - `docs/render.yaml`
- passos_atomicos:
  1. revisar cada arquivo alvo procurando instrucoes que ainda coloquem PostgreSQL local como requisito padrao
  2. marcar quais trechos devem ser atualizados para refletir Supabase como banco unico
  3. preservar as excecoes legitimas de testes com SQLite e qualquer observacao que continue relevante para o backend
  4. consolidar o inventario de drift antes de editar os documentos
- comandos_permitidos:
  - `rg -n "postgresql@16|createdb npbb|DATABASE_URL|DIRECT_URL|Supabase|SQLite|TESTING" backend/.env.example docs/SETUP.md docs/TROUBLESHOOTING.md docs/DEPLOY_RENDER_CLOUDFLARE.md docs/render.yaml`
- resultado_esperado: inventario fechado das inconsistencias documentais e de configuracao
- testes_ou_validacoes_obrigatorias:
  - confirmar que o inventario cobre setup, troubleshooting, deploy e exemplo de env
- stop_conditions:
  - parar se surgir dependencia operacional nova nao validada em F3

### T2
- objetivo: atualizar os artefatos de configuracao e setup para refletir o Supabase como banco unico do projeto
- precondicoes: T1 concluida; inventario de drift fechado
- arquivos_a_ler_ou_tocar:
  - `backend/.env.example`
  - `docs/SETUP.md`
  - `scripts/dev_backend.sh`
- passos_atomicos:
  1. alinhar `backend/.env.example` ao papel final de `DATABASE_URL` e `DIRECT_URL`
  2. ajustar `docs/SETUP.md` para remover PostgreSQL local como requisito operacional principal e deixar claro o fallback de testes
  3. conferir se o launcher oficial em `scripts/dev_backend.sh` continua coerente com o setup resultante
  4. manter fora do escopo qualquer alteracao de frontend ou Supabase Auth
- comandos_permitidos:
  - `rg -n "DATABASE_URL|DIRECT_URL|postgresql@16|createdb npbb" backend/.env.example docs/SETUP.md scripts/dev_backend.sh`
- resultado_esperado: configuracao e setup alinhados ao Supabase como banco unico
- testes_ou_validacoes_obrigatorias:
  - confirmar que o setup final ainda preserva `TESTING=true` como caminho de SQLite para testes
- stop_conditions:
  - parar se a mudanca documental exigir alterar o contrato validado de runtime do backend

### T3
- objetivo: alinhar troubleshooting e deploy ao estado final do banco unico validado em F3
- precondicoes: T2 concluida
- arquivos_a_ler_ou_tocar:
  - `docs/TROUBLESHOOTING.md`
  - `docs/DEPLOY_RENDER_CLOUDFLARE.md`
  - `docs/render.yaml`
  - `backend/.env.example`
- passos_atomicos:
  1. ajustar `docs/TROUBLESHOOTING.md` para refletir o novo caminho principal de banco e os gotchas realmente restantes
  2. revisar `docs/DEPLOY_RENDER_CLOUDFLARE.md` e `docs/render.yaml` para garantir coerencia com o contrato final de `DATABASE_URL` e `DIRECT_URL`
  3. confirmar que deploy e troubleshooting nao reintroduzem PostgreSQL local como dependencia principal
  4. preservar as instrucoes de go-live ja existentes que continuam validas
- comandos_permitidos:
  - `rg -n "DATABASE_URL|DIRECT_URL|Postgres|Supabase|Render" docs/TROUBLESHOOTING.md docs/DEPLOY_RENDER_CLOUDFLARE.md docs/render.yaml backend/.env.example`
- resultado_esperado: troubleshooting e deploy coerentes com o Supabase como banco unico
- testes_ou_validacoes_obrigatorias:
  - confirmar que deploy, setup e troubleshooting descrevem o mesmo contrato de banco
- stop_conditions:
  - parar se houver contradicao entre o estado final validado e o que a documentacao de deploy permite publicar

### T4
- objetivo: executar a revisao final de consistencia entre todos os arquivos atualizados
- precondicoes: T3 concluida
- arquivos_a_ler_ou_tocar:
  - `backend/.env.example`
  - `docs/SETUP.md`
  - `docs/TROUBLESHOOTING.md`
  - `docs/DEPLOY_RENDER_CLOUDFLARE.md`
  - `docs/render.yaml`
- passos_atomicos:
  1. comparar os cinco arquivos lado a lado quanto ao papel de `DATABASE_URL`, `DIRECT_URL`, Supabase e SQLite em testes
  2. remover contradicoes residuais ou repeticoes que desviem do estado final validado
  3. confirmar que o PostgreSQL local nao aparece mais como requisito operacional padrao
  4. liberar a issue somente com um estado documental coerente entre setup, troubleshooting e deploy
- comandos_permitidos:
  - `rg -n "postgresql@16|createdb npbb|DATABASE_URL|DIRECT_URL|SQLite|Supabase" backend/.env.example docs/SETUP.md docs/TROUBLESHOOTING.md docs/DEPLOY_RENDER_CLOUDFLARE.md docs/render.yaml`
- resultado_esperado: conjunto documental final coerente com o Supabase como banco unico
- testes_ou_validacoes_obrigatorias:
  - confirmar que nao restou instrucao principal para operar o backend com PostgreSQL local
- stop_conditions:
  - parar se ainda houver contradicao material entre setup, troubleshooting e deploy

## Arquivos Reais Envolvidos
- `backend/.env.example`
- `docs/SETUP.md`
- `docs/TROUBLESHOOTING.md`
- `docs/DEPLOY_RENDER_CLOUDFLARE.md`
- `docs/render.yaml`
- `scripts/dev_backend.sh`

## Artifact Minimo

Conjunto final de configuracao e documentacao coerente com o Supabase como banco
unico do projeto.

## Dependencias
- [Intake](../../INTAKE-SUPABASE.md)
- [Epic](../EPIC-F3-02-Consolidar-Configuracao-Final-e-Remover-Dependencia-do-Postgres-Local.md)
- [Fase](../F3_SUPABASE_EPICS.md)
- [PRD](../../PRD-SUPABASE.md)
- [EPIC-F3-01](../EPIC-F3-01-Validar-Backend-e-Scripts-Criticos-contra-Supabase.md)
