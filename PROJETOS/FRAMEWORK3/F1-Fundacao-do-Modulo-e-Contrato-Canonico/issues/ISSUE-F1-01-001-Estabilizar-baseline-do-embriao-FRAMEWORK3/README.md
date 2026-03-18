---
doc_id: "ISSUE-F1-01-001-Estabilizar-baseline-do-embriao-FRAMEWORK3"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-01-001 - Estabilizar baseline do embriao FRAMEWORK3

## User Story

Como PM do FRAMEWORK3, quero estabilizar baseline do embriao framework3 para baseline do backend importando com o router framework habilitado e smoke test rastreavel.

## Contexto Tecnico

Esta issue materializa o recorte mais urgente do projeto. No estado atual do repositorio `backend/app/services/framework_orchestrator.py` importa `app.core.config` inexistente e isso quebra o import de `backend/app/main.py` quando o router framework e carregado. Os arquivos listados abaixo concentram o contrato que precisa ser consolidado neste passo do FRAMEWORK3. As precondicoes das tasks explicitam a ordem obrigatoria dentro da fase e da sprint.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem o recorte "Estabilizar baseline do embriao FRAMEWORK3"
- Green: alinhamento minimo do recorte para entregar baseline do backend importando com o router framework habilitado e smoke test rastreavel
- Refactor: consolidar nomes contratos e rastreabilidade sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given o contexto e as dependencias desta issue, When as tasks previstas forem executadas, Then o recorte "Estabilizar baseline do embriao FRAMEWORK3" fica materializado sem ampliar o escopo aprovado.
- Given os arquivos e validacoes listados, When os comandos e checks obrigatorios forem executados, Then baseline do backend importando com o router framework habilitado e smoke test rastreavel.
- Given a issue concluida, When epico fase e sprint forem revisados, Then nao resta ambiguidade operacional relevante para este recorte.

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Estabilizar boot e smoke do backend com router framework](./TASK-1.md)

## Arquivos Reais Envolvidos
- `backend/app/services/framework_orchestrator.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/app/main.py`
- `backend/tests/test_framework_startup.py`

## Artifact Minimo

Baseline do backend importando com o router framework habilitado e smoke test rastreavel.

## Dependencias
- [Intake](../../../INTAKE-FRAMEWORK3.md)
- [Epic](../../EPIC-F1-01-Modelo-Canonico-do-Framework3.md)
- [Fase](../../F1_FRAMEWORK3_EPICS.md)
- [PRD](../../../PRD-FRAMEWORK3.md)
- dependencias_operacionais: nenhuma
