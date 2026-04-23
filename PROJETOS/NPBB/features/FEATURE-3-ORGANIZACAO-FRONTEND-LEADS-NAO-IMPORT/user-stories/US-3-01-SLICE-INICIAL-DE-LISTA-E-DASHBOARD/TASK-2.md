---
doc_id: "TASK-2.md"
user_story_id: "US-3-01-SLICE-INICIAL-DE-LISTA-E-DASHBOARD"
task_id: "T2"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-22"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "plano_organizacao_import.md"
  - "PROJETOS/NPBB/INTAKE-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md"
  - "PROJETOS/NPBB/PRD-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md"
  - "PROJETOS/NPBB/features/FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT/**"
tdd_aplicavel: false
---

# T2 - Registrar `DashboardLeads.tsx` como artefato legado nao roteado

## objetivo

Formalizar em governanca e no plano local que `frontend/src/pages/DashboardLeads.tsx`
permanece como artefato legado, sem rota publica e fora do slice executado.

## passos_atomicos

1. abrir os artefatos `INTAKE`, `PRD` e `FEATURE-3`
2. registrar `DashboardLeads.tsx` como legado nao roteado
3. manter manifesto e rotas sem alteracao funcional

## comandos_permitidos

- `rg -n "DashboardLeads|leads/conversao|analise-etaria" PROJETOS frontend/src plano_organizacao_import.md`

## stop_conditions

- parar se a documentacao exigir religar rota ou habilitar manifesto
