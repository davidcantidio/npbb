---
doc_id: "ISSUE-F1-01-002-CRIAR-MIGRATION-ALEMBIC-PARA-NOVOS-CAMPOS-DO-LEAD.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-F1-01-002 - Criar migration Alembic para novos campos do Lead

## User Story

Como engenheiro de backend do dashboard, quero entregar Criar migration Alembic para novos campos do Lead para cumprir o objetivo tecnico do epico sem quebrar o contrato ja definido para o dashboard.

## Contexto Tecnico

Gerar e validar migration Alembic que adiciona as colunas `is_cliente_bb` e
`is_cliente_estilo` à tabela `lead`. Ambos os campos são incluídos na mesma migration
por afinidade semântica.

A implementacao materializada nesta issue e a revision
`8a7c5d4e3f21_add_bb_flags_to_lead.py`, ja integrada a arvore Alembic atual.

Como o `head` avancou apos a criacao da issue, a validacao operacional foi executada
contra o intervalo `7f3c2d1b4a6e -> 8a7c5d4e3f21`, preservando o comportamento exigido
para upgrade, criacao de indices e downgrade da migration desta issue.

## Plano TDD

- Red: criar ou ajustar testes para reproduzir a lacuna descrita nos criterios de aceitacao.
- Green: implementar o comportamento minimo necessario para fazer os testes passarem.
- Refactor: consolidar nomes, extracoes e contratos sem ampliar o escopo da issue.

## Criterios de Aceitacao

- [x] Arquivo de migration em `backend/alembic/versions/` com revision ID único
- [x] `alembic upgrade head` aplica sem erro em banco limpo
- [x] `alembic upgrade head` aplica sem erro em banco com dados existentes
- [x] `alembic downgrade -1` remove as colunas sem efeito colateral
- [x] Índices `ix_lead_is_cliente_bb` e `ix_lead_is_cliente_estilo` criados

## Definition of Done da Issue

- [x] Arquivo de migration em `backend/alembic/versions/` com revision ID único
- [x] `alembic upgrade head` aplica sem erro em banco limpo
- [x] `alembic upgrade head` aplica sem erro em banco com dados existentes
- [x] `alembic downgrade -1` remove as colunas sem efeito colateral
- [x] Índices `ix_lead_is_cliente_bb` e `ix_lead_is_cliente_estilo` criados

## Tarefas Decupadas

- [x] T1: Gerar migration com `alembic revision --autogenerate -m "add_is_cliente_bb_estilo_to_lead"`
- [x] T2: Revisar migration gerada — verificar que apenas os campos esperados aparecem
- [x] T3: Testar upgrade em banco limpo
- [x] T4: Testar upgrade em banco com leads existentes (verificar NULLs)
- [x] T5: Testar downgrade

## Arquivos Reais Envolvidos

- `backend/alembic/versions/8a7c5d4e3f21_add_bb_flags_to_lead.py`
- `alembic.ini`

## Artifact Minimo

- `backend/alembic/versions/8a7c5d4e3f21_add_bb_flags_to_lead.py`

## Dependencias

- [Issue Dependente](./ISSUE-F1-01-001-ADICIONAR-CAMPOS-IS-CLIENTE-BB-E-IS-CLIENTE-ESTILO-AO-MODELO-LEAD.md)
- [Epic](../EPIC-F1-01-EXTENSAO-MODELO-LEAD.md)
- [Fase](../F1_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [PRD](../../PRD-DASHBOARD-LEADS-ETARIA.md)

## Navegacao Rapida

- `[[../EPIC-F1-01-EXTENSAO-MODELO-LEAD]]`
- `[[../../PRD-DASHBOARD-LEADS-ETARIA]]`
