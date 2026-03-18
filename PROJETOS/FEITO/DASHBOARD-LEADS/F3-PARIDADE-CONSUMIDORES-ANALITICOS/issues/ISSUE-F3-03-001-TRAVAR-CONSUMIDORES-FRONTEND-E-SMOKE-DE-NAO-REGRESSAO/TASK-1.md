---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F3-03-001-TRAVAR-CONSUMIDORES-FRONTEND-E-SMOKE-DE-NAO-REGRESSAO"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# T1 - Travar consumidores frontend e smoke de nao regressao

## objetivo

Validar consumidores React e servicos frontend sem alterar payloads ou UX fora do escopo do PRD.

## precondicoes

- README da issue lido integralmente
- PRD e epic da fase consultados antes de alterar qualquer arquivo
- dependencias declaradas na issue satisfeitas

## arquivos_a_ler_ou_tocar

- `frontend/src/services/dashboard_age_analysis.ts`
- `frontend/src/services/dashboard_leads.ts`
- `frontend/src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.filters.test.tsx`
- `frontend/src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.states.test.tsx`
- `frontend/src/pages/dashboard/__tests__/DashboardModule.test.tsx`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir o contrato principal de `ISSUE-F3-03-001` no modulo alvo
  - cobrir um caso de regressao ligado ao paradigma canonico `LeadEvento`
- comando_para_rodar:
  - `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.filters.test.tsx src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.states.test.tsx src/pages/dashboard/__tests__/DashboardModule.test.tsx`
- criterio_red:
  - os testes novos devem falhar antes da implementacao; se ja passarem sem mudanca de codigo, parar e revisar a task

## passos_atomicos

1. escrever ou ajustar primeiro os testes focados listados em `testes_red`
2. rodar o comando red e confirmar falha ligada ao comportamento esperado da issue
3. implementar o minimo necessario nos arquivos alvo para satisfazer apenas o contrato descrito
4. rodar novamente a suite alvo e confirmar green
5. refatorar nomes, imports ou duplicacoes locais sem ampliar escopo

## comandos_permitidos

- `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.filters.test.tsx src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.states.test.tsx src/pages/dashboard/__tests__/DashboardModule.test.tsx`
- `rg -n "lead_evento|LeadEvento|LeadEventoSourceKind|AtivacaoLead|evento_nome|lead_batch|manual_reconciled|dashboard" frontend/src/services/dashboard_age_analysis.ts frontend/src/services/dashboard_leads.ts frontend/src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.filters.test.tsx frontend/src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.states.test.tsx`

## resultado_esperado

Os consumidores frontend continuam compatveis com os contratos atuais do backend apos a consolidacao canonica.

## testes_ou_validacoes_obrigatorias

- smoke do modulo dashboard permanece verde
- consumidores de analise etaria e leads continuam aceitando o payload atual

## stop_conditions

- parar se surgir requisito novo nao previsto no PRD ou no README da issue
- parar se o comando alvo falhar por motivo estrutural nao relacionado a escopo local
