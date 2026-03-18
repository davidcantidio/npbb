---
doc_id: "ISSUE-F4-01-001-REMOVER-HEURISTICOS-RESIDUAIS-E-CODIGO-MORTO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F4-01-001 - Remover heuristicos residuais e codigo morto

## User Story

Como mantenedor do modulo de leads e dashboards, quero remover heuristicos residuais e codigo morto para que a remediacao do vinculo canonico fique consistente e auditavel dentro de `EPIC-F4-01`.

## Contexto Tecnico

- a issue fecha o drift tecnico restante depois que F3 estabiliza o comportamento externo
- issue pertence a `EPIC-F4-01` na fase `F4` do projeto `DASHBOARD-LEADS`
- artefato minimo esperado: O codigo principal de leitura por evento deixa de expor residuos do caminho heuristico superado.

## Plano TDD

- Red: escrever ou ajustar testes focados nos contratos diretamente afetados por `ISSUE-F4-01-001` usando `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_dashboard_age_analysis_endpoint.py tests/test_dashboard_leads_endpoint.py tests/test_dashboard_leads_report_endpoint.py` como comando alvo.
- Green: implementar o minimo necessario para fazer os testes novos passarem sem ampliar escopo fora da issue.
- Refactor: remover drift local, nomes confusos ou duplicacoes mantendo a suite alvo green.

## Criterios de Aceitacao

- Given os arquivos alvo de `ISSUE-F4-01-001`, When a issue for concluida, Then o codigo principal de leitura por evento deixa de expor residuos do caminho heuristico superado.
- Given a dependencia das issues anteriores, When a validacao final rodar, Then a entrega nao reintroduz o paradigma antigo de `Lead -> AtivacaoLead -> Evento` como obrigatorio
- Given o modo `required`, When outro agente ler a issue, Then `README.md` e `TASK-1.md` bastam para executar a entrega sem improvisar escopo

## Definition of Done da Issue

- [ ] O codigo principal de leitura por evento deixa de expor residuos do caminho heuristico superado.
- [ ] validacao final obrigatoria executada ou preparada no comando alvo da issue
- [ ] dependencias e links canonicos da issue mantidos coerentes com fase e epic

## Tasks

- [T1: Remover heuristicos residuais e codigo morto](./TASK-1.md)

## Arquivos Reais Envolvidos

- `backend/app/services/dashboard_service.py`
- `backend/app/services/lead_event_service.py`
- `backend/app/routers/dashboard_leads.py`

## Artifact Minimo

O codigo principal de leitura por evento deixa de expor residuos do caminho heuristico superado.

## Dependencias

- [Intake](../../../INTAKE-DASHBOARD-LEADS.md)
- [PRD](../../../PRD-DASHBOARD-LEADS.md)
- [Fase](../../F4_DASHBOARD_LEADS_EPICS.md)
- [Epic](../../EPIC-F4-01-RETIRADA-CONTROLADA-DO-HEURISTICO.md)
