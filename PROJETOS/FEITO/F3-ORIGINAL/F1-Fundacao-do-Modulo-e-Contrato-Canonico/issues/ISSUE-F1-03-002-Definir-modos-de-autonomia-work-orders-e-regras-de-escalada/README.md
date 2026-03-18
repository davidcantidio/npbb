---
doc_id: "ISSUE-F1-03-002-Definir-modos-de-autonomia-work-orders-e-regras-de-escalada"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-03-002 - Definir modos de autonomia work orders e regras de escalada

## User Story

Como PM do FRAMEWORK3, quero definir modos de autonomia work orders e regras de escalada para contrato operacional de autonomia e work order aprovado para o framework3.

## Contexto Tecnico

O algoritmo do FRAMEWORK3 exige combinacao de HITL e automacao configuravel por projeto. Esta issue fecha os modos de autonomia e os criterios de escalada. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: nao se aplica como suite automatizada dominante; validar primeiro as divergencias e lacunas do recorte
- Green: fechar o contrato documental ou operacional minimo para entregar modos de autonomia criterios de parada e payload minimo de work order aprovados
- Refactor: consolidar linguagem e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Definir modos de autonomia work orders e regras de escalada" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then modos de autonomia criterios de parada e payload minimo de work order aprovados.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Definir modos de autonomia e regras de escalada](./TASK-1.md)

## Arquivos Reais Envolvidos
- `PROJETOS/COMUM/GOV-WORK-ORDER.md`
- `PROJETOS/FRAMEWORK3/PRD-FRAMEWORK3.md`
- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`

## Artifact Minimo

Modos de autonomia criterios de parada e payload minimo de work order aprovados.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F1-03-Contrato-do-AgentOrchestrator-e-Modos-de-Operacao.md)
- [Fase](../../F1_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F1-03-001, ISSUE-F1-02-001
