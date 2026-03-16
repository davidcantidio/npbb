---
doc_id: "ISSUE-F3-01-001-Validar-Runtime-do-Backend-com-Supabase"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-16"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F3-01-001 - Validar runtime do backend com Supabase

## User Story

Como operador do backend, quero validar a API usando o Supabase como banco de
runtime, para confirmar que o cutover do banco suporta o fluxo real da
aplicacao.

## Contexto Tecnico

`backend/app/db/database.py` define o contrato de runtime da aplicacao e
`scripts/dev_backend.sh` e o launcher oficial a partir da raiz do repo. Depois
da recarga de dados em F2, esta issue confirma que a API sobe e responde usando
`DATABASE_URL` do Supabase, mantendo `DIRECT_URL` reservada para operacoes
sensiveis de banco.

## Plano TDD
- Red: falhar se a API subir apontando para um banco local ou com contrato de URL incoerente
- Green: levantar o backend com as URLs do Supabase e validar o fluxo basico de runtime
- Refactor: consolidar os bloqueios objetivos que restarem antes da documentacao final

## Criterios de Aceitacao
- Given `DATABASE_URL` e `DIRECT_URL` do Supabase configuradas, When a API e iniciada, Then o backend sobe usando o Supabase como banco de runtime
- Given a API em execucao, When os checks basicos de disponibilidade forem feitos, Then os endpoints minimos respondem como esperado
- Given a validacao de runtime concluida, When a documentacao final for ajustada, Then o estado operacional validado esta claro

## Definition of Done da Issue
- [x] backend iniciado com `DATABASE_URL` do Supabase
- [x] checks minimos de disponibilidade executados com sucesso
- [x] bloqueios objetivos de runtime registrados, se existirem

## Tasks

- [T1: Preparar ambiente e conferir contrato de URLs](./TASK-1.md)
- [T2: Iniciar API e executar checks de disponibilidade](./TASK-2.md)
- [T3: Consolidar resultado para documentacao final](./TASK-3.md)

## Arquivos Reais Envolvidos

- `backend/app/db/database.py`
- `backend/.env.example`
- `scripts/dev_backend.sh`
- `docs/DEPLOY_RENDER_CLOUDFLARE.md`
- `docs/TROUBLESHOOTING.md`

## Artifact Minimo

Backend validado em runtime com o Supabase como banco de aplicacao.

## Dependencias

- [Intake](../../../INTAKE-SUPABASE.md)
- [Epic](../../EPIC-F3-01-Validar-Backend-e-Scripts-Criticos-contra-Supabase.md)
- [Fase](../../F3_SUPABASE_EPICS.md)
- [PRD](../../../PRD-SUPABASE.md)
- [F2](../../../F2-Migracao-de-Dados/F2_SUPABASE_EPICS.md)
