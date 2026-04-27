---
doc_id: "US-9-01-DECIDIR-SHELL-IMPORTACAO-LEADS"
version: "1.0"
status: "ready_for_review"
owner: "PM"
last_updated: "2026-04-23"
task_instruction_mode: "required"
feature_id: "FEATURE-9-DECISAO-SHELL-IMPORTACAO-LEADS"
decision_refs:
  - "plano_organizacao_import.md"
  - "PRD-DECISAO-SHELL-IMPORTACAO-LEADS.md"
---

# US-9-01 - Decidir shell de importacao de leads

## User Story

Como engenharia do NPBB, quero registrar a fronteira atual do shell
`/leads/importar`, para que uma reorganizacao futura de importacao seja feita
com escopo proprio e sem arrastar ETL funcional.

## Feature de Origem

- **Feature**: `FEATURE-9-DECISAO-SHELL-IMPORTACAO-LEADS`
- **Comportamento coberto**: decisao documental sobre o shell frontend de
  importacao, preservando comportamento e contratos atuais

## Contexto Tecnico

`FEATURE-8` removeu wrappers nao-import e fez as rotas internas de lista e
analise etaria consumirem diretamente `frontend/src/features/leads`. O bloco de
importacao permanece em `frontend/src/pages/leads`, com `ImportacaoPage.tsx`
puxando componentes locais e telas de mapeamento/pipeline.

## Criterios de Aceitacao (Given / When / Then)

- **Given** a rota `/leads/importar`,
  **when** `AppRoutes.tsx` for revisado,
  **then** o lazy import continua apontando para
  `../pages/leads/ImportacaoPage`.
- **Given** o shell de importacao,
  **when** a decisao for registrada,
  **then** `ImportacaoPage.tsx` permanece em `frontend/src/pages/leads` nesta
  rodada.
- **Given** os subfluxos acoplados,
  **when** o inventario for registrado,
  **then** `frontend/src/pages/leads/importacao/**`, `MapeamentoPage`,
  `BatchMapeamentoPage` e `PipelineStatusPage` aparecem como dependencias
  atuais.
- **Given** o freeze de importacao/ETL,
  **when** a task terminar,
  **then** nenhum contrato HTTP, schema, backend, ETL funcional,
  `lead_pipeline/` ou `core/leads_etl/` foi alterado pela feature.
- **Given** as mudancas locais de dashboard preexistentes,
  **when** a task terminar,
  **then** elas permanecem fora do diff desta feature.

## Tasks

- [T1 - Registrar decisao do shell de importacao](./TASK-1.md)

## Arquivos Reais Envolvidos

- `plano_organizacao_import.md`
- `PROJETOS/NPBB/INTAKE-DECISAO-SHELL-IMPORTACAO-LEADS.md`
- `PROJETOS/NPBB/PRD-DECISAO-SHELL-IMPORTACAO-LEADS.md`
- `PROJETOS/NPBB/features/FEATURE-9-DECISAO-SHELL-IMPORTACAO-LEADS/**`

## Dependencias

- [PRD decisao shell importacao leads](../../../../PRD-DECISAO-SHELL-IMPORTACAO-LEADS.md)
- [Intake decisao shell importacao leads](../../../../INTAKE-DECISAO-SHELL-IMPORTACAO-LEADS.md)
- [Plano operacional](../../../../../plano_organizacao_import.md)
