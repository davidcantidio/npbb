---
doc_id: "ISSUE-F1-01-002-Fechar-contrato-canonico-de-entidades-IDs-e-estados"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-01-002 - Fechar contrato canonico de entidades IDs e estados

## User Story

Como PM do FRAMEWORK3, quero fechar contrato canonico de entidades ids e estados para dominio framework3 alinhado a taxonomias ids e estados canonicos com modelos e schemas coerentes.

## Contexto Tecnico

Depois de estabilizar a baseline o projeto precisa alinhar a estrutura persistida do dominio a governanca canonicamente aprovada. Esta issue fecha taxonomias IDs estados e o reflexo disso em modelos e schemas. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Fechar contrato canonico de entidades IDs e estados"
- Green: alinhamento minimo do recorte para entregar contrato canonico do dominio framework3 refletido em modelos schemas e migration
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Fechar contrato canonico de entidades IDs e estados" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then contrato canonico do dominio FRAMEWORK3 refletido em modelos schemas e migration.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Fechar contrato canonicode entidades estados e taxonomias](./TASK-1.md)
- [T2 - Materializar contrato aprovado em models schemas e migration](./TASK-2.md)

## Arquivos Reais Envolvidos
- `PROJETOS/FRAMEWORK3/INTAKE-FRAMEWORK3.md`
- `PROJETOS/FRAMEWORK3/PRD-FRAMEWORK3.md`
- `PROJETOS/COMUM/GOV-INTAKE.md`
- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/alembic/versions/c0d63429d56d_add_lead_evento_table_for_issue_f1_01_.py`
- `backend/tests/test_framework_domain_contract.py`

## Artifact Minimo

Contrato canonico do dominio FRAMEWORK3 refletido em modelos schemas e migration.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F1-01-Modelo-Canonico-do-Framework3.md)
- [Fase](../../F1_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F1-01-001
