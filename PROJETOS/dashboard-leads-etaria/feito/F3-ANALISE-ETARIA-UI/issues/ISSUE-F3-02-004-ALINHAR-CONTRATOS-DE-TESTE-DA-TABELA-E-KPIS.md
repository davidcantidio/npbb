---
doc_id: "ISSUE-F3-02-004-ALINHAR-CONTRATOS-DE-TESTE-DA-TABELA-E-KPIS.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
task_instruction_mode: "required"
---

# ISSUE-F3-02-004 - Alinhar contratos de teste da tabela e KPIs

## User Story

Como engenheiro de frontend da analise etaria, quero reconciliar o contrato de exibicao
da tabela e dos KPI cards com a suite de testes para remover o `hold` da auditoria
F3-R01 e restabelecer rastreabilidade de qualidade.

## Contexto Tecnico

A rodada F3-R01 detectou falhas bloqueantes em:

- `src/components/dashboard/__tests__/EventsAgeTable.test.tsx`
- `src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.states.test.tsx`

As falhas mostram drift entre o que os testes validam e o contrato efetivamente
renderizado (texto/celulas BB/KPI labels). O ajuste deve alinhar componente e teste sem
mascarar lacunas funcionais reais.

> Observacao: o estado loading completo segue sob responsabilidade de
> `ISSUE-F3-02-002`; esta issue cobre especificamente o contrato tabela/KPI.

## Plano TDD

- Red: reproduzir as falhas atuais de `EventsAgeTable` e KPI/estados correlatos.
- Green: alinhar contrato de renderizacao e asserts para passar sem perder cobertura.
- Refactor: reduzir duplicacao de regras de formatacao entre testes e componentes.

## Criterios de Aceitacao

- [x] `EventsAgeTable.test.tsx` passa com asserts coerentes para formato de valores BB e dados parciais.
- [x] `LeadsAgeAnalysisPage.states.test.tsx` passa nos cenarios de KPI cards sem depender de labels divergentes.
- [x] Labels de KPI e valores exibidos permanecem aderentes ao PRD/F3 e a utilitarios de formatacao.
- [x] Ajustes nao desabilitam nem afrouxam os cenarios criticos de regressao.

## Definition of Done da Issue

- [x] Todos os criterios de aceitacao validados localmente
- [x] Falhas bloqueantes da auditoria F3-R01 relacionadas a contrato tabela/KPI eliminadas
- [x] Evidencia de teste anexada no fechamento da issue

## Tarefas Decupadas

- [x] T1: Revisar contratos atuais de renderizacao em `EventsAgeTable` e `AgeAnalysisKpiGrid`.
- [x] T2: Ajustar implementacao e/ou asserts para convergencia deterministica de labels/formato.
- [x] T3: Executar testes de tabela e estados da pagina com foco nos cenarios que falharam na auditoria.
- [x] T4: Registrar resultados e vincular fechamento ao relatorio F3-R01.

## Instructions por Task

### T1 - Revisar contrato atual

1. Mapear diferencas entre valores renderizados e matchers usados nos testes.
2. Priorizar nomes/formatos definidos pelos utilitarios de formatacao do modulo.

### T2 - Implementar alinhamento

1. Corrigir no componente quando houver desvio funcional real.
2. Corrigir no teste quando a divergencia for apenas de matcher/texto legado.

### T3 - Rodar suite alvo

1. Executar ao menos:
   `EventsAgeTable.test.tsx` e `LeadsAgeAnalysisPage.states.test.tsx`.
2. Confirmar ausencia de regressao nos testes de `InfoTooltip`.

### T4 - Consolidar rastreabilidade

1. Atualizar issue com comandos executados e resultado.
2. Referenciar explicitamente `RELATORIO-AUDITORIA-F3-R01`.

## Arquivos Reais Envolvidos

- `frontend/src/components/dashboard/EventsAgeTable.tsx`
- `frontend/src/components/dashboard/AgeAnalysisKpiGrid.tsx`
- `frontend/src/components/dashboard/__tests__/EventsAgeTable.test.tsx`
- `frontend/src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.states.test.tsx`

## Artifact Minimo

- `frontend/src/components/dashboard/__tests__/EventsAgeTable.test.tsx`

## Evidencia de Validacao

- comando: `cd /Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/frontend && npm run test -- --run src/components/dashboard/__tests__/EventsAgeTable.test.tsx src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.states.test.tsx src/components/dashboard/__tests__/InfoTooltip.test.tsx`
- resultado: `3 arquivos, 14 testes passando`

## Dependencias

- [Issue Dependente](./ISSUE-F3-02-002-IMPLEMENTAR-ESTADOS-DA-INTERFACE-LOADING-EMPTY-ERROR.md)
- [Epic](../EPIC-F3-02-COBERTURA-ESTADOS-QUALIDADE.md)
- [Fase](../F3_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [Auditoria](../auditorias/RELATORIO-AUDITORIA-F3-R01.md)

## Navegacao Rapida

- `[[./ISSUE-F3-02-002-IMPLEMENTAR-ESTADOS-DA-INTERFACE-LOADING-EMPTY-ERROR]]`
- `[[../EPIC-F3-02-COBERTURA-ESTADOS-QUALIDADE]]`
- `[[../auditorias/RELATORIO-AUDITORIA-F3-R01]]`
