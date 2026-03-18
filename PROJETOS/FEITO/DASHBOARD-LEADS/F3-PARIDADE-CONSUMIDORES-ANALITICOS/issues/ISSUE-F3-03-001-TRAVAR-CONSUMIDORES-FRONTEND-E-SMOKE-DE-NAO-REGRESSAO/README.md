---
doc_id: "ISSUE-F3-03-001-TRAVAR-CONSUMIDORES-FRONTEND-E-SMOKE-DE-NAO-REGRESSAO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F3-03-001 - Travar consumidores frontend e smoke de nao regressao

## User Story

Como mantenedor do modulo de leads e dashboards, quero travar consumidores frontend e smoke de nao regressao para que a remediacao do vinculo canonico fique consistente e auditavel dentro de `EPIC-F3-03`.

## Contexto Tecnico

- essa issue e de travamento de contrato, nao de redesign visual
- issue pertence a `EPIC-F3-03` na fase `F3` do projeto `DASHBOARD-LEADS`
- artefato minimo esperado: Os consumidores frontend continuam compatveis com os contratos atuais do backend apos a consolidacao canonica.

## Plano TDD

- Red: escrever ou ajustar testes focados nos contratos diretamente afetados por `ISSUE-F3-03-001` usando `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.filters.test.tsx src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.states.test.tsx src/pages/dashboard/__tests__/DashboardModule.test.tsx` como comando alvo.
- Green: implementar o minimo necessario para fazer os testes novos passarem sem ampliar escopo fora da issue.
- Refactor: remover drift local, nomes confusos ou duplicacoes mantendo a suite alvo green.

## Criterios de Aceitacao

- Given os arquivos alvo de `ISSUE-F3-03-001`, When a issue for concluida, Then os consumidores frontend continuam compatveis com os contratos atuais do backend apos a consolidacao canonica.
- Given a dependencia das issues anteriores, When a validacao final rodar, Then a entrega nao reintroduz o paradigma antigo de `Lead -> AtivacaoLead -> Evento` como obrigatorio
- Given o modo `required`, When outro agente ler a issue, Then `README.md` e `TASK-1.md` bastam para executar a entrega sem improvisar escopo

## Definition of Done da Issue

- [ ] Os consumidores frontend continuam compatveis com os contratos atuais do backend apos a consolidacao canonica.
- [ ] validacao final obrigatoria executada ou preparada no comando alvo da issue
- [ ] dependencias e links canonicos da issue mantidos coerentes com fase e epic

## Tasks

- [T1: Travar consumidores frontend e smoke de nao regressao](./TASK-1.md)

## Arquivos Reais Envolvidos

- `frontend/src/services/dashboard_age_analysis.ts`
- `frontend/src/services/dashboard_leads.ts`
- `frontend/src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.filters.test.tsx`
- `frontend/src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.states.test.tsx`
- `frontend/src/pages/dashboard/__tests__/DashboardModule.test.tsx`

## Artifact Minimo

Os consumidores frontend continuam compatveis com os contratos atuais do backend apos a consolidacao canonica.

## Dependencias

- [Intake](../../../INTAKE-DASHBOARD-LEADS.md)
- [PRD](../../../PRD-DASHBOARD-LEADS.md)
- [Fase](../../F3_DASHBOARD_LEADS_EPICS.md)
- [Epic](../../EPIC-F3-03-CONTRATO-FRONTEND-E-SMOKE-DE-NAO-REGRESSAO.md)
- [Issue Dependente](../ISSUE-F3-01-002-VALIDAR-PARIDADE-DA-ANALISE-ETARIA/README.md)
- [Issue Dependente](../ISSUE-F3-02-001-CONSOLIDAR-DASHBOARD-LEADS-E-RANKINGS/README.md)
- [Issue Dependente](../ISSUE-F3-02-002-CONSOLIDAR-DASHBOARD-LEADS-RELATORIO/README.md)
