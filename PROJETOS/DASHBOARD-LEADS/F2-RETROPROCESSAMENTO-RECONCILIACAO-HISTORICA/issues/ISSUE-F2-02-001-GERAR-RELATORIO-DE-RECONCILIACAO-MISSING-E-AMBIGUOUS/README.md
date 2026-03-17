---
doc_id: "ISSUE-F2-02-001-GERAR-RELATORIO-DE-RECONCILIACAO-MISSING-E-AMBIGUOUS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-02-001 - Gerar relatorio de reconciliacao missing e ambiguous

## User Story

Como mantenedor do modulo de leads e dashboards, quero gerar relatorio de reconciliacao missing e ambiguous para que a remediacao do vinculo canonico fique consistente e auditavel dentro de `EPIC-F2-02`.

## Contexto Tecnico

- o PRD nao autoriza inferencia silenciosa de evento em historico ambiguo
- issue pertence a `EPIC-F2-02` na fase `F2` do projeto `DASHBOARD-LEADS`
- artefato minimo esperado: Existe relatorio rastreavel com volumes e referencias para os casos historicos nao resolvidos.

## Plano TDD

- Red: escrever ou ajustar testes focados nos contratos diretamente afetados por `ISSUE-F2-02-001` usando `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_lead_event_service.py -k reconcile` como comando alvo.
- Green: implementar o minimo necessario para fazer os testes novos passarem sem ampliar escopo fora da issue.
- Refactor: remover drift local, nomes confusos ou duplicacoes mantendo a suite alvo green.

## Criterios de Aceitacao

- Given os arquivos alvo de `ISSUE-F2-02-001`, When a issue for concluida, Then existe relatorio rastreavel com volumes e referencias para os casos historicos nao resolvidos.
- Given a dependencia das issues anteriores, When a validacao final rodar, Then a entrega nao reintroduz o paradigma antigo de `Lead -> AtivacaoLead -> Evento` como obrigatorio
- Given o modo `required`, When outro agente ler a issue, Then `README.md` e `TASK-1.md` bastam para executar a entrega sem improvisar escopo

## Definition of Done da Issue

- [ ] Existe relatorio rastreavel com volumes e referencias para os casos historicos nao resolvidos.
- [ ] validacao final obrigatoria executada ou preparada no comando alvo da issue
- [ ] dependencias e links canonicos da issue mantidos coerentes com fase e epic

## Tasks

- [T1: Gerar relatorio de reconciliacao missing e ambiguous](./TASK-1.md)

## Arquivos Reais Envolvidos

- `backend/app/services/lead_event_service.py`
- `backend/tests/test_lead_event_service.py`
- `artifacts/lead_evento_reconciliation/`

## Artifact Minimo

Existe relatorio rastreavel com volumes e referencias para os casos historicos nao resolvidos.

## Dependencias

- [Intake](../../../INTAKE-DASHBOARD-LEADS.md)
- [PRD](../../../PRD-DASHBOARD-LEADS.md)
- [Fase](../../F2_DASHBOARD_LEADS_EPICS.md)
- [Epic](../../EPIC-F2-02-RECONCILIACAO-DE-CASOS-AMBIGUOS-E-NAO-RESOLVIDOS.md)
- [Issue Dependente](../ISSUE-F2-01-001-IMPLEMENTAR-RUNNER-IDEMPOTENTE-DE-BACKFILL/README.md)
