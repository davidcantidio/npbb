---
doc_id: "ISSUE-F1-01-003-ATUALIZAR-SCHEMAS-DE-LEITURA-DO-LEAD.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-F1-01-003 - Atualizar schemas de leitura do Lead

## User Story

Como engenheiro de backend do dashboard, quero entregar Atualizar schemas de leitura do Lead para cumprir o objetivo tecnico do epico sem quebrar o contrato ja definido para o dashboard.

## Contexto Tecnico

Atualizar os schemas Pydantic de leitura do Lead (`LeadListItemRead` e similares) para
incluir os novos campos `is_cliente_bb` e `is_cliente_estilo`, garantindo que a
serialização JSON não quebre fluxos existentes.

Sem observacoes adicionais alem das dependencias e restricoes do epico.

## Plano TDD

- Red: criar ou ajustar testes para reproduzir a lacuna descrita nos criterios de aceitacao.
- Green: implementar o comportamento minimo necessario para fazer os testes passarem.
- Refactor: consolidar nomes, extracoes e contratos sem ampliar o escopo da issue.

## Criterios de Aceitacao

- [x] `LeadListItemRead` inclui `is_cliente_bb: Optional[bool]` e `is_cliente_estilo: Optional[bool]`
- [x] Outros schemas de leitura do Lead que exponham dados atualizados conforme necessário
- [x] Serialização de leads antigos (campos NULL) funciona sem erro
- [x] Endpoints existentes que retornam leads continuam funcionais

## Definition of Done da Issue

- [x] `LeadListItemRead` inclui `is_cliente_bb: Optional[bool]` e `is_cliente_estilo: Optional[bool]`
- [x] Outros schemas de leitura do Lead que exponham dados atualizados conforme necessário
- [x] Serialização de leads antigos (campos NULL) funciona sem erro
- [x] Endpoints existentes que retornam leads continuam funcionais

## Tarefas Decupadas

- [x] T1: Localizar todos os schemas de leitura do Lead em `backend/app/schemas/`
- [x] T2: Adicionar campos opcionais aos schemas relevantes
- [x] T3: Executar testes existentes de endpoints que retornam leads
- [x] T4: Verificar que a documentação OpenAPI reflete os novos campos

## Arquivos Reais Envolvidos

- `backend/app/schemas/`
- `backend/tests/`

## Artifact Minimo

- `backend/app/schemas/`

## Dependencias

- [Issue Dependente](./ISSUE-F1-01-001-ADICIONAR-CAMPOS-IS-CLIENTE-BB-E-IS-CLIENTE-ESTILO-AO-MODELO-LEAD.md)
- [Epic](../EPIC-F1-01-EXTENSAO-MODELO-LEAD.md)
- [Fase](../F1_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [PRD](../../PRD-DASHBOARD-LEADS-ETARIA.md)

## Navegacao Rapida

- `[[../EPIC-F1-01-EXTENSAO-MODELO-LEAD]]`
- `[[../../PRD-DASHBOARD-LEADS-ETARIA]]`
