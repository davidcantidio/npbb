---
doc_id: "ISSUE-F3-01-002-EXECUTAR-COM-AUTONOMIA-CONFIGURAVEL-E-ACOMPANHAMENTO-OPERACIONAL"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F3-01-002 - Executar com autonomia configuravel e acompanhamento operacional

## User Story

Como PM, quero definir autonomia, override humano e acompanhamento operacional para executar issues e tasks com seguranca.

## Feature de Origem

- **Feature**: Feature 4
- **Comportamento coberto**: politica de autonomia, disparo controlado, override humano e evidencias operacionais

## Contexto Tecnico

Depois da selecao da unidade elegivel, o dominio precisa fechar os modos de autonomia, registrar work orders e acompanhar execucao com evidencias e bloqueios.

## Plano TDD
- Red: escrever primeiro os testes e checks que cobrem politica de autonomia, execucao e evidencias
- Green: alinhar dominio API e UI para disparo controlado e acompanhamento operacional
- Refactor: consolidar estados e mensagens do fluxo sem ampliar o escopo da issue

## Criterios de Aceitacao
- Given uma unidade elegivel, When a politica de autonomia permitir, Then a execucao segue com registro de work order e evidencias
- Given uma situacao de override, When o PM intervir, Then o sistema registra decisao, motivo e novo estado
- Given a issue concluida, When o historico operacional for consultado, Then execucoes, bloqueios e outputs ficam rastreaveis

## Definition of Done da Issue
- [ ] todas as tasks da issue estao `done`
- [ ] validacoes obrigatorias do recorte foram executadas ou revisadas
- [ ] o artifact minimo da issue foi produzido e ficou rastreavel
- [ ] dependencias e links internos do manifesto foram conferidos

## Tasks
- [T1 - Definir politicas de autonomia, escalada e estados de execucao](./TASK-1.md)
- [T2 - Integrar disparo e registro de execucao com evidencias](./TASK-2.md)
- [T3 - Entregar acompanhamento operacional com override do PM](./TASK-3.md)

## Arquivos Reais Envolvidos
- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/app/services/framework_orchestrator.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/tests/test_framework_execution_flow.py`
- `frontend/src/services/framework.ts`
- `frontend/src/types/framework.ts`
- `frontend/src/pages/dashboard/FrameworkExecutionPage.tsx`
- `frontend/src/components/dashboard/FrameworkExecutionPanel.tsx`
- `frontend/src/pages/dashboard/__tests__/FrameworkExecutionPage.test.tsx`

## Artifact Minimo

Fluxo operacional com autonomia configuravel, override humano e evidencias persistidas.

## Dependencias
- [Intake](../../../INTAKE-FW5.md)
- [Epic](../../EPIC-F3-01-EXECUCAO-ASSISTIDA-COM-AUTONOMIA-CONTROLADA.md)
- [Fase](../../F3_FW5_EPICS.md)
- [PRD](../../../PRD-FW5.md)
- dependencias_operacionais: ISSUE-F3-01-001
