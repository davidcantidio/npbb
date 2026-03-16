---
doc_id: "ISSUE-F3-02-001-Atualizar-Configuracao-e-Documentacao-para-Supabase-como-Banco-Unico"
version: "1.0"
status: "active"
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

## Tasks

- [x] [T1: Mapear pontos de drift documental e de configuracao](./TASK-1.md) — [INVENTARIO-DRIFT.md](./INVENTARIO-DRIFT.md)
- [x] [T2: Atualizar configuracao e setup para Supabase como banco unico](./TASK-2.md)
- [T3: Alinhar troubleshooting e deploy ao estado final validado](./TASK-3.md)
- [T4: Revisao final de consistencia entre arquivos atualizados](./TASK-4.md)

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

- [Intake](../../../INTAKE-SUPABASE.md)
- [Epic](../../EPIC-F3-02-Consolidar-Configuracao-Final-e-Remover-Dependencia-do-Postgres-Local.md)
- [Fase](../../F3_SUPABASE_EPICS.md)
- [PRD](../../../PRD-SUPABASE.md)
- [EPIC-F3-01](../../EPIC-F3-01-Validar-Backend-e-Scripts-Criticos-contra-Supabase.md)
