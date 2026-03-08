---
doc_id: "ISSUE-F1-01-001-ADICIONAR-CAMPOS-IS-CLIENTE-BB-E-IS-CLIENTE-ESTILO-AO-MODELO-LEAD.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-F1-01-001 - Adicionar campos `is_cliente_bb` e `is_cliente_estilo` ao modelo Lead

## User Story

Como engenheiro de backend do dashboard, quero entregar Adicionar campos `is_cliente_bb` e `is_cliente_estilo` ao modelo Lead para cumprir o objetivo tecnico do epico sem quebrar o contrato ja definido para o dashboard.

## Contexto Tecnico

Estender o SQLModel `Lead` com dois campos boolean nullable para armazenar o resultado
do cruzamento com a base de dados do Banco do Brasil. Ambos os campos recebem índice
individual para otimizar queries do dashboard.

Os campos seguem o mesmo padrão de campos nullable já existentes no modelo. A description
do Field deve explicar a semântica: "True = cliente BB confirmado; NULL = cruzamento pendente".

## Plano TDD

- Red: criar ou ajustar testes para reproduzir a lacuna descrita nos criterios de aceitacao.
- Green: implementar o comportamento minimo necessario para fazer os testes passarem.
- Refactor: consolidar nomes, extracoes e contratos sem ampliar o escopo da issue.

## Criterios de Aceitacao

- [x] Classe `Lead` possui campo `is_cliente_bb: Optional[bool] = Field(default=None, index=True)`
- [x] Classe `Lead` possui campo `is_cliente_estilo: Optional[bool] = Field(default=None, index=True)`
- [x] Campos têm description explicativa no Field
- [x] Leads existentes continuam válidos (default NULL)
- [x] Testes de criação de lead com e sem os novos campos passam

## Definition of Done da Issue

- [x] Classe `Lead` possui campo `is_cliente_bb: Optional[bool] = Field(default=None, index=True)`
- [x] Classe `Lead` possui campo `is_cliente_estilo: Optional[bool] = Field(default=None, index=True)`
- [x] Campos têm description explicativa no Field
- [x] Leads existentes continuam válidos (default NULL)
- [x] Testes de criação de lead com e sem os novos campos passam

## Tarefas Decupadas

- [x] T1: Adicionar campos ao modelo `Lead` em `backend/app/models/models.py`
- [x] T2: Verificar que imports e tipagem estão corretos (Optional, Field)
- [x] T3: Executar testes existentes do modelo Lead para garantir retrocompatibilidade

## Arquivos Reais Envolvidos

- `backend/app/models/models.py`
- `backend/tests/`

## Artifact Minimo

- `backend/app/models/models.py`

## Dependencias

- [Epic](../EPIC-F1-01-EXTENSAO-MODELO-LEAD.md)
- [Fase](../F1_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [PRD](../../PRD-DASHBOARD-LEADS-ETARIA.md)

## Navegacao Rapida

- `[[../EPIC-F1-01-EXTENSAO-MODELO-LEAD]]`
- `[[../../PRD-DASHBOARD-LEADS-ETARIA]]`
