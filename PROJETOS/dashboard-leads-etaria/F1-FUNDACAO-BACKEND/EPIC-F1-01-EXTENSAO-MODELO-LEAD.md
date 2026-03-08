---
doc_id: "EPIC-F1-01-EXTENSAO-MODELO-LEAD.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# EPIC-F1-01 - Extensao do Modelo Lead e Migracao

## Objetivo

Adicionar ao modelo `Lead` os campos `is_cliente_bb` e `is_cliente_estilo` (boolean
nullable), criar a migration Alembic correspondente e atualizar os schemas de
leitura/escrita para expor os novos campos sem quebrar fluxos existentes.

**Contexto:** Os campos representam o resultado de cruzamento externo com a base do
Banco do Brasil. Ficam `NULL` até que o cruzamento seja realizado para o lote
correspondente. O dashboard usa esses campos para calcular percentuais de clientes BB
e cobertura de dados.

## Resultado de Negocio Mensuravel

O backend passa a expor os campos de cobertura BB de forma retrocompativel, permitindo o uso do dashboard sem quebrar fluxos existentes.

## Contexto Arquitetural

- Modelo `Lead` em `backend/app/models/models.py` (SQLModel, table=True)
- Migrations Alembic em `backend/alembic/versions/`
- Schemas Pydantic em `backend/app/schemas/`
- PYTHONPATH: `/workspace:/workspace/backend`
- Ambos os campos são indexados para performance de queries do dashboard

## Definition of Done do Epico

- [x] Model `Lead` possui `is_cliente_bb` e `is_cliente_estilo` (Optional[bool], default=None, indexed)
- [x] Migration Alembic criada e aplicável em banco limpo e com dados existentes
- [x] Rollback da migration remove os campos sem efeito colateral
- [x] Schemas de leitura do Lead atualizados para incluir os novos campos
- [x] Testes de criação/leitura de lead com e sem os novos campos passam

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-01-001 | Adicionar campos `is_cliente_bb` e `is_cliente_estilo` ao modelo Lead | Adicionar campos `is_cliente_bb` e `is_cliente_estilo` ao modelo Lead | 3 | done | [ISSUE-F1-01-001-ADICIONAR-CAMPOS-IS-CLIENTE-BB-E-IS-CLIENTE-ESTILO-AO-MODELO-LEAD.md](./issues/ISSUE-F1-01-001-ADICIONAR-CAMPOS-IS-CLIENTE-BB-E-IS-CLIENTE-ESTILO-AO-MODELO-LEAD.md) |
| ISSUE-F1-01-002 | Criar migration Alembic para novos campos do Lead | Criar migration Alembic para novos campos do Lead | 2 | done | [ISSUE-F1-01-002-CRIAR-MIGRATION-ALEMBIC-PARA-NOVOS-CAMPOS-DO-LEAD.md](./issues/ISSUE-F1-01-002-CRIAR-MIGRATION-ALEMBIC-PARA-NOVOS-CAMPOS-DO-LEAD.md) |
| ISSUE-F1-01-003 | Atualizar schemas de leitura do Lead | Atualizar schemas de leitura do Lead | 2 | done | [ISSUE-F1-01-003-ATUALIZAR-SCHEMAS-DE-LEITURA-DO-LEAD.md](./issues/ISSUE-F1-01-003-ATUALIZAR-SCHEMAS-DE-LEITURA-DO-LEAD.md) |

## Artifact Minimo do Epico

- `backend/app/models/models.py`
- `backend/alembic/versions/`
- `backend/app/schemas/`

## Dependencias

- [PRD](../PRD-DASHBOARD-LEADS-ETARIA.md)
- [Fase](./F1_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [Decision Protocol](../DECISION-PROTOCOL.md)

## Notas de Implementacao Globais

- Os dois campos devem ser tratados como par semântico — sempre adicionados juntos
- Não criar índice composto nesta fase; avaliar após medição de performance em produção
- Manter retrocompatibilidade total: nenhum endpoint existente deve quebrar

## Navegacao Rapida

- `[[./issues/ISSUE-F1-01-001-ADICIONAR-CAMPOS-IS-CLIENTE-BB-E-IS-CLIENTE-ESTILO-AO-MODELO-LEAD]]`
- `[[./issues/ISSUE-F1-01-002-CRIAR-MIGRATION-ALEMBIC-PARA-NOVOS-CAMPOS-DO-LEAD]]`
- `[[./issues/ISSUE-F1-01-003-ATUALIZAR-SCHEMAS-DE-LEITURA-DO-LEAD]]`
- `[[../PRD-DASHBOARD-LEADS-ETARIA]]`
