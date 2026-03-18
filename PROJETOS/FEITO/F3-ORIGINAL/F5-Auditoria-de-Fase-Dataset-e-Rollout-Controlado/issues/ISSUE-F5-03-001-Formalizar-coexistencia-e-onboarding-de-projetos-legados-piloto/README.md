---
doc_id: "ISSUE-F5-03-001-Formalizar-coexistencia-e-onboarding-de-projetos-legados-piloto"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F5-03-001 - Formalizar coexistencia e onboarding de projetos legados piloto

## User Story

Como PM do FRAMEWORK3, quero formalizar coexistencia e onboarding de projetos legados piloto para protocolo de coexistencia e onboarding de projetos legados aprovado.

## Contexto Tecnico

Antes do rollout o modulo precisa definir como convive com projetos legados e como um piloto entra no fluxo sem migracao em massa. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: nao se aplica como suite automatizada dominante; validar primeiro as divergencias e lacunas do recorte
- Green: fechar o contrato documental ou operacional minimo para entregar politica de coexistencia com legados e onboarding do piloto definida
- Refactor: consolidar linguagem e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Formalizar coexistencia e onboarding de projetos legados piloto" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then politica de coexistencia com legados e onboarding do piloto definida.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Formalizar coexistencia com legados e onboarding do piloto](./TASK-1.md)

## Arquivos Reais Envolvidos
- `PROJETOS/FRAMEWORK3/PRD-FRAMEWORK3.md`
- `PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md`
- `PROJETOS/COMUM/GOV-ISSUE-FIRST.md`
- `backend/app/models/framework_models.py`

## Artifact Minimo

Politica de coexistencia com legados e onboarding do piloto definida.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F5-03-Rollout-Coexistencia-e-Piloto-Operacional.md)
- [Fase](../../F5_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F1-02-001
