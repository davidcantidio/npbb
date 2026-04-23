---
doc_id: "US-7-01-REMOVER-ALIAS-LEADS-PUBLICIDADE"
version: "1.0"
status: "ready_for_review"
owner: "PM"
last_updated: "2026-04-23"
task_instruction_mode: "required"
feature_id: "FEATURE-7-REMOCAO-ALIAS-LEADS-PUBLICIDADE"
decision_refs:
  - "plano_organizacao_import.md"
  - "PRD-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md"
  - "PRD-REMOCAO-ALIAS-LEADS-PUBLICIDADE.md"
---

# US-7-01 - Remover alias leads publicidade

## User Story

Como engenharia do NPBB, quero remover o alias temporario
`app.modules.leads_publicidade`, para que o backend de importacao de leads tenha
um unico caminho interno suportado em `app.modules.lead_imports`.

## Feature de Origem

- **Feature**: `FEATURE-7-REMOCAO-ALIAS-LEADS-PUBLICIDADE`
- **Comportamento coberto**: limpeza estrutural do alias temporario depois do
  rename fisico implementado na `FEATURE-6`

## Contexto Tecnico

`FEATURE-6` tornou `app.modules.lead_imports` o pacote real e preservou
`app.modules.leads_publicidade` como compatibilidade temporaria. A busca atual
confirma ausencia de consumidores ativos fora dos shims e do teste dedicado,
permitindo fechar a janela de compatibilidade.

## Criterios de Aceitacao (Given / When / Then)

- **Given** consumidores ativos,
  **when** a busca excluindo shims e teste dedicado for executada,
  **then** nao ha ocorrencias de `app.modules.leads_publicidade`.
- **Given** o pacote backend,
  **when** a implementacao for revisada,
  **then** `backend/app/modules/leads_publicidade` nao existe.
- **Given** os testes backend,
  **when** a implementacao for revisada,
  **then** `backend/tests/test_lead_imports_compat.py` nao existe.
- **Given** consumidores ativos,
  **when** os imports forem revisados,
  **then** routers, worker, servicos e testes focados usam
  `app.modules.lead_imports`.
- **Given** o escopo da rodada,
  **when** a task terminar,
  **then** nenhum contrato HTTP, schema, rota, frontend, dashboard,
  `lead_pipeline/` ou `core/leads_etl/` foi alterado pela feature.

## Tasks

- [T1 - Remover alias legado leads_publicidade](./TASK-1.md)

## Arquivos Reais Envolvidos

- `backend/app/modules/leads_publicidade/**`
- `backend/tests/test_lead_imports_compat.py`
- `plano_organizacao_import.md`
- `PROJETOS/NPBB/INTAKE-REMOCAO-ALIAS-LEADS-PUBLICIDADE.md`
- `PROJETOS/NPBB/PRD-REMOCAO-ALIAS-LEADS-PUBLICIDADE.md`
- `PROJETOS/NPBB/features/FEATURE-7-REMOCAO-ALIAS-LEADS-PUBLICIDADE/**`

## Dependencias

- [PRD remocao alias leads publicidade](../../../../PRD-REMOCAO-ALIAS-LEADS-PUBLICIDADE.md)
- [Intake remocao alias leads publicidade](../../../../INTAKE-REMOCAO-ALIAS-LEADS-PUBLICIDADE.md)
- [Plano operacional](../../../../../plano_organizacao_import.md)
