---
doc_id: "US-4-01-ARQUIVAR-DASHBOARD-LEADS-LEGADO"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-23"
task_instruction_mode: "required"
feature_id: "FEATURE-4-DECISAO-DASHBOARD-LEADS-LEGADO"
decision_refs:
  - "plano_organizacao_import.md"
---

# US-4-01 - Arquivar DashboardLeads legado

## User Story

Como engenharia do NPBB, quero remover a tela frontend legada
`DashboardLeads.tsx` e seu servico exclusivo, para evitar que codigo sem rota
publica continue sendo interpretado como superficie ativa ou reaproveitavel sem
decisao de produto.

## Feature de Origem

- **Feature**: `FEATURE-4-DECISAO-DASHBOARD-LEADS-LEGADO`
- **Comportamento coberto**: limpeza da superficie frontend orfa de dashboard
  de leads

## Contexto Tecnico

`DashboardLeads.tsx` foi documentado em `FEATURE-3` como legado nao roteado. A
busca atual confirmou que o servico `dashboard_leads.ts` e exclusivo dessa
tela, enquanto `/dashboard/leads/conversao` permanece apenas como entrada
desabilitada no manifesto.

Esta US remove o codigo frontend orfao e preserva o endpoint backend
`GET /dashboard/leads/relatorio`, que segue disponivel para script/uso
programatico sem tela roteada.

## Criterios de Aceitacao (Given / When / Then)

- **Given** o frontend,
  **when** a limpeza terminar,
  **then** `DashboardLeads.tsx` e `dashboard_leads.ts` nao existem mais em
  `frontend/src`.
- **Given** o dashboard atual,
  **when** rotas e manifesto forem avaliados,
  **then** `/dashboard/leads/analise-etaria` continua habilitada e
  `/dashboard/leads/conversao` continua desabilitada.
- **Given** o backend de relatorio,
  **when** a limpeza frontend terminar,
  **then** `GET /dashboard/leads/relatorio` permanece fora do diff funcional.

## Tasks

- [T1 - Remover superficie frontend orfa de DashboardLeads](./TASK-1.md)

## Arquivos Reais Envolvidos

- `frontend/src/pages/DashboardLeads.tsx`
- `frontend/src/services/dashboard_leads.ts`
- `plano_organizacao_import.md`
- `PROJETOS/NPBB/INTAKE-DECISAO-DASHBOARD-LEADS-LEGADO.md`
- `PROJETOS/NPBB/PRD-DECISAO-DASHBOARD-LEADS-LEGADO.md`

## Dependencias

- [PRD decisao DashboardLeads legado](../../../../PRD-DECISAO-DASHBOARD-LEADS-LEGADO.md)
- [Feature 3](../../../FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT/FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md)
