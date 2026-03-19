---
doc_id: "ISSUE-F3-02-001-CONSOLIDAR-DASHBOARD-LEADS-RELATORIO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-19"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F3-02-001 - Consolidar /dashboard/leads/relatorio

## User Story

Como mantenedor do modulo de leads e dashboards, quero consolidar /dashboard/leads/relatorio para que a remediacao do vinculo canonico fique consistente e auditavel dentro de `EPIC-F3-02`.


## Feature de Origem

- **Feature**: Feature 2
- **Comportamento coberto**: relatorio agregado coerente por evento.

## Contexto Tecnico

- o relatorio agregado nao pode divergir da semantica dos outros consumidores por evento
- issue pertence a `EPIC-F3-02` na fase `F3` do projeto `DL2`
- artefato minimo esperado: O relatorio agregado preserva payload e filtros atuais apoiado na base canonica.

## Plano TDD

- Red: escrever ou ajustar testes focados nos contratos diretamente afetados por `ISSUE-F3-02-001` usando `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_dashboard_leads_report_endpoint.py` como comando alvo.
- Green: implementar o minimo necessario para fazer os testes novos passarem sem ampliar escopo fora da issue.
- Refactor: remover drift local, nomes confusos ou duplicacoes mantendo a suite alvo green.

## Criterios de Aceitacao

- Given os arquivos alvo de `ISSUE-F3-02-001`, When a issue for concluida, Then o relatorio agregado preserva payload e filtros atuais apoiado na base canonica.
- Given a dependencia das issues anteriores, When a validacao final rodar, Then a entrega nao reintroduz o paradigma antigo de `Lead -> AtivacaoLead -> Evento` como obrigatorio
- Given o modo `required`, When outro agente ler a issue, Then `README.md` e `TASK-1.md` bastam para executar a entrega sem improvisar escopo

## Definition of Done da Issue

- [ ] O relatorio agregado preserva payload e filtros atuais apoiado na base canonica.
- [ ] validacao final obrigatoria executada ou preparada no comando alvo da issue
- [ ] dependencias e links canonicos da issue mantidos coerentes com fase e epic

## Tasks

- [T1: Consolidar /dashboard/leads/relatorio](./TASK-1.md)

## Arquivos Reais Envolvidos

- `backend/app/services/dashboard_leads_report.py`
- `backend/app/routers/dashboard_leads.py`
- `backend/tests/test_dashboard_leads_report_endpoint.py`

## Artifact Minimo

O relatorio agregado preserva payload e filtros atuais apoiado na base canonica.

## Dependencias

- [Intake](../../../INTAKE-DL2.md)
- [PRD](../../../PRD-DL2.md)
- [Fase](../../F3_DL2_EPICS.md)
- [Epic](../../EPIC-F3-02-RELATORIO-AGREGADO-COERENTE-POR-EVENTO.md)
