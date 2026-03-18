---
doc_id: "ISSUE-F2-02-002-FORMALIZAR-FECHAMENTO-MANUAL-RECONCILED.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-02-002 - Formalizar fechamento manual_reconciled

## User Story

Como mantenedor do modulo de leads e dashboards, quero formalizar fechamento manual_reconciled para que a remediacao do vinculo canonico fique consistente e auditavel dentro de `EPIC-F2-02`.

## Contexto Tecnico

- o enum `manual_reconciled` ja existe no modelo e precisa de caminho util no projeto
- issue pertence a `EPIC-F2-02` na fase `F2` do projeto `DASHBOARD-LEADS`
- artefato minimo esperado: Existe caminho explicito para registrar `manual_reconciled` sem perder rastreabilidade do fechamento manual.

## Plano TDD

- Red: escrever ou ajustar testes focados nos contratos diretamente afetados por `ISSUE-F2-02-002` usando `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_lead_event_service.py -k manual_reconciled` como comando alvo.
- Green: implementar o minimo necessario para fazer os testes novos passarem sem ampliar escopo fora da issue.
- Refactor: remover drift local, nomes confusos ou duplicacoes mantendo a suite alvo green.

## Criterios de Aceitacao

- Given os arquivos alvo de `ISSUE-F2-02-002`, When a issue for concluida, Then existe caminho explicito para registrar `manual_reconciled` sem perder rastreabilidade do fechamento manual.
- Given a dependencia das issues anteriores, When a validacao final rodar, Then a entrega nao reintroduz o paradigma antigo de `Lead -> AtivacaoLead -> Evento` como obrigatorio
- Given o modo `required`, When outro agente ler a issue, Then `README.md` e `TASK-1.md` bastam para executar a entrega sem improvisar escopo

## Definition of Done da Issue

- [ ] Existe caminho explicito para registrar `manual_reconciled` sem perder rastreabilidade do fechamento manual.
- [ ] validacao final obrigatoria executada ou preparada no comando alvo da issue
- [ ] dependencias e links canonicos da issue mantidos coerentes com fase e epic

## Tasks

- [T1: Formalizar fechamento manual_reconciled](./TASK-1.md)

## Arquivos Reais Envolvidos

- `backend/app/services/lead_event_service.py`
- `backend/tests/test_lead_event_service.py`

## Artifact Minimo

Existe caminho explicito para registrar `manual_reconciled` sem perder rastreabilidade do fechamento manual.

## Dependencias

- [Intake](../../../INTAKE-DASHBOARD-LEADS.md)
- [PRD](../../../PRD-DASHBOARD-LEADS.md)
- [Fase](../../F2_DASHBOARD_LEADS_EPICS.md)
- [Epic](../../EPIC-F2-02-RECONCILIACAO-DE-CASOS-AMBIGUOS-E-NAO-RESOLVIDOS.md)
- [Issue Dependente](../ISSUE-F2-02-001-GERAR-RELATORIO-DE-RECONCILIACAO-MISSING-E-AMBIGUOUS/README.md)
