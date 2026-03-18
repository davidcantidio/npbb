---
doc_id: "EPIC-F1-03-Contrato-do-AgentOrchestrator-e-Modos-de-Operacao.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
---

# EPIC-F1-03 - Contrato do AgentOrchestrator e Modos de Operacao

## Objetivo

Formalizar a maquina de estados os gates HITL os work orders e os modos de autonomia por projeto.

## Resultado de Negocio Mensuravel

Estados work orders e modos de autonomia deixam de depender de inferencia implicita e passam a ter contrato unico no FRAMEWORK3.

## Contexto Arquitetural

O algoritmo do projeto exige gates humanos obrigatorios e tambem modos configuraveis de autonomia. Este epic alinha o servico de orquestracao ao fluxo canonico antes das fases de CRUD e execucao.

## Definition of Done do Epico
- [ ] transicoes validas e invalidas de estado estao definidas
- [ ] gates HITL e criterios de escalada estao documentados no dominio
- [ ] modos de autonomia e payload minimo de work order foram aprovados

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-03-001 | Definir maquina de estados e gates HITL do orquestrador | Estados e gates operacionais sem ambiguidade no dominio framework. | 1 | todo | [ISSUE-F1-03-001-Definir-maquina-de-estados-e-gates-HITL-do-orquestrador](./issues/ISSUE-F1-03-001-Definir-maquina-de-estados-e-gates-HITL-do-orquestrador/) |
| ISSUE-F1-03-002 | Definir modos de autonomia work orders e regras de escalada | Contrato operacional de autonomia e work order aprovado para o FRAMEWORK3. | 1 | todo | [ISSUE-F1-03-002-Definir-modos-de-autonomia-work-orders-e-regras-de-escalada](./issues/ISSUE-F1-03-002-Definir-modos-de-autonomia-work-orders-e-regras-de-escalada/) |

## Artifact Minimo do Epico

Contrato operacional do orquestrador pronto para sustentar planejamento e execucao.

## Dependencias
- [Intake](../INTAKE-FRAMEWORK3.md)
- [PRD](../PRD-FRAMEWORK3.md)
- [Fase](./F1_FRAMEWORK3_EPICS.md)
- dependencias operacionais:
- EPIC-F1-01
- EPIC-F1-02
