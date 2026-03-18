---
doc_id: "ISSUE-F1-02-001-Formalizar-sincronizacao-precedencia-e-bootstrap-Markdown-banco"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-02-001 - Formalizar sincronizacao precedencia e bootstrap Markdown-banco

## User Story

Como PM do FRAMEWORK3, quero formalizar sincronizacao precedencia e bootstrap markdown-banco para projeto framework3 nasce com fonte de verdade declarada bootstrap minimo e estado de sincronizacao observavel.

## Contexto Tecnico

O PRD ainda deixa aberta a precedencia entre artefato Markdown e base persistida. Esta issue fecha o contrato de bootstrap do projeto e o reflexo disso no backend. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Formalizar sincronizacao precedencia e bootstrap Markdown-banco"
- Green: alinhamento minimo do recorte para entregar protocolo de bootstrap e sincronizacao markdown-banco aplicado ao dominio framework
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Formalizar sincronizacao precedencia e bootstrap Markdown-banco" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then protocolo de bootstrap e sincronizacao Markdown-banco aplicado ao dominio framework.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Definir precedencia e bootstrap minimo do projeto](./TASK-1.md)
- [T2 - Aplicar contrato de sincronizacao e bootstrapping no backend](./TASK-2.md)

## Arquivos Reais Envolvidos
- `PROJETOS/COMUM/GOV-ISSUE-FIRST.md`
- `PROJETOS/COMUM/GOV-WORK-ORDER.md`
- `PROJETOS/FRAMEWORK3/INTAKE-FRAMEWORK3.md`
- `PROJETOS/FRAMEWORK3/PRD-FRAMEWORK3.md`
- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_sync_contract.py`

## Artifact Minimo

Protocolo de bootstrap e sincronizacao Markdown-banco aplicado ao dominio framework.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F1-02-Coexistencia-Markdown-Banco-e-Rastreabilidade.md)
- [Fase](../../F1_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: ISSUE-F1-01-002
