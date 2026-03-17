---
doc_id: "ISSUE-F1-04-001-ALINHAR-FIXTURES-E-SUITE-AO-MODELO-CANONICO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-04-001 - Alinhar fixtures e suite ao modelo canonico

## User Story

Como mantenedor do modulo de leads e dashboards, quero alinhar fixtures e suite ao modelo canonico para que a remediacao do vinculo canonico fique consistente e auditavel dentro de `EPIC-F1-04`.

## Contexto Tecnico

- a cobertura precisa deixar de depender apenas de `AtivacaoLead`
- essa issue fecha a baseline auditavel da fase
- issue pertence a `EPIC-F1-04` na fase `F1` do projeto `DASHBOARD-LEADS`
- artefato minimo esperado: As suites de dashboard passam a refletir explicitamente o modelo canonico `LeadEvento`.

## Plano TDD

- Red: escrever ou ajustar testes focados nos contratos diretamente afetados por `ISSUE-F1-04-001` usando `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_dashboard_age_analysis_endpoint.py tests/test_dashboard_leads_endpoint.py tests/test_dashboard_leads_report_endpoint.py` como comando alvo.
- Green: implementar o minimo necessario para fazer os testes novos passarem sem ampliar escopo fora da issue.
- Refactor: remover drift local, nomes confusos ou duplicacoes mantendo a suite alvo green.

## Criterios de Aceitacao

- Given os arquivos alvo de `ISSUE-F1-04-001`, When a issue for concluida, Then as suites de dashboard passam a refletir explicitamente o modelo canonico `LeadEvento`.
- Given a dependencia das issues anteriores, When a validacao final rodar, Then a entrega nao reintroduz o paradigma antigo de `Lead -> AtivacaoLead -> Evento` como obrigatorio
- Given o modo `required`, When outro agente ler a issue, Then `README.md` e `TASK-1.md` bastam para executar a entrega sem improvisar escopo

## Definition of Done da Issue

- [ ] As suites de dashboard passam a refletir explicitamente o modelo canonico `LeadEvento`.
- [ ] validacao final obrigatoria executada ou preparada no comando alvo da issue
- [ ] dependencias e links canonicos da issue mantidos coerentes com fase e epic

## Tasks

- [T1: Alinhar fixtures e suite ao modelo canonico](./TASK-1.md)

## Arquivos Reais Envolvidos

- `backend/tests/test_dashboard_age_analysis_endpoint.py`
- `backend/tests/test_dashboard_leads_endpoint.py`
- `backend/tests/test_dashboard_leads_report_endpoint.py`

## Artifact Minimo

As suites de dashboard passam a refletir explicitamente o modelo canonico `LeadEvento`.

## Dependencias

- [Intake](../../../INTAKE-DASHBOARD-LEADS.md)
- [PRD](../../../PRD-DASHBOARD-LEADS.md)
- [Fase](../../F1_DASHBOARD_LEADS_EPICS.md)
- [Epic](../../EPIC-F1-04-COBERTURA-EXECUTAVEL-E-INVARIANTES-DO-VINCULO.md)
- [Issue Dependente](../ISSUE-F1-02-002-COBRIR-DUPLICATA-DE-CONVERSAO-E-INVARIANTES-DO-SUBMIT/README.md)
- [Issue Dependente](../ISSUE-F1-03-001-GARANTIR-LEAD-EVENTO-NO-PIPELINE-GOLD/README.md)
- [Issue Dependente](../ISSUE-F1-03-002-GARANTIR-LEAD-EVENTO-NO-ETL-POR-EVENTO-NOME/README.md)
