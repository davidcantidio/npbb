---
doc_id: "ISSUE-F3-02-001-CONSOLIDAR-DASHBOARD-LEADS-E-RANKINGS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F3-02-001 - Consolidar /dashboard/leads e rankings

## User Story

Como mantenedor do modulo de leads e dashboards, quero consolidar /dashboard/leads e rankings para que a remediacao do vinculo canonico fique consistente e auditavel dentro de `EPIC-F3-02`.

## Contexto Tecnico

- essa consolidacao precisa refletir a mesma semantica do restante do dashboard
- issue pertence a `EPIC-F3-02` na fase `F3` do projeto `DASHBOARD-LEADS`
- artefato minimo esperado: O endpoint `/dashboard/leads` e seus rankings ficam consolidados sobre a leitura canonica.

## Plano TDD

- Red: escrever ou ajustar testes focados nos contratos diretamente afetados por `ISSUE-F3-02-001` usando `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_dashboard_leads_endpoint.py` como comando alvo.
- Green: implementar o minimo necessario para fazer os testes novos passarem sem ampliar escopo fora da issue.
- Refactor: remover drift local, nomes confusos ou duplicacoes mantendo a suite alvo green.

## Criterios de Aceitacao

- Given os arquivos alvo de `ISSUE-F3-02-001`, When a issue for concluida, Then o endpoint `/dashboard/leads` e seus rankings ficam consolidados sobre a leitura canonica.
- Given a dependencia das issues anteriores, When a validacao final rodar, Then a entrega nao reintroduz o paradigma antigo de `Lead -> AtivacaoLead -> Evento` como obrigatorio
- Given o modo `required`, When outro agente ler a issue, Then `README.md` e `TASK-1.md` bastam para executar a entrega sem improvisar escopo

## Definition of Done da Issue

- [ ] O endpoint `/dashboard/leads` e seus rankings ficam consolidados sobre a leitura canonica.
- [ ] validacao final obrigatoria executada ou preparada no comando alvo da issue
- [ ] dependencias e links canonicos da issue mantidos coerentes com fase e epic

## Tasks

- [T1: Consolidar /dashboard/leads e rankings](./TASK-1.md)

## Arquivos Reais Envolvidos

- `backend/app/routers/dashboard_leads.py`
- `backend/app/utils/dashboard_rankings.py`
- `backend/tests/test_dashboard_leads_endpoint.py`

## Artifact Minimo

O endpoint `/dashboard/leads` e seus rankings ficam consolidados sobre a leitura canonica.

## Dependencias

- [Intake](../../../INTAKE-DASHBOARD-LEADS.md)
- [PRD](../../../PRD-DASHBOARD-LEADS.md)
- [Fase](../../F3_DASHBOARD_LEADS_EPICS.md)
- [Epic](../../EPIC-F3-02-CONSOLIDACAO-DOS-ENDPOINTS-AGREGADOS-DE-LEADS.md)
