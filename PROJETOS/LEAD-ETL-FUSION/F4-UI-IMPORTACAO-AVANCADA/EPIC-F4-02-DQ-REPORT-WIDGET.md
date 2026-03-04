---
doc_id: "EPIC-F4-02-DQ-REPORT-WIDGET"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# EPIC-F4-02 - DQ Report Widget

## Objetivo

Construir o componente de DQ report no frontend, exibindo `check_name`, `severity`, `affected_rows` e `sample`, e governando o botao "Importar mesmo assim" com base em `warning` versus `error`.

## Resultado de Negocio Mensuravel

Usuarios deixam de aprovar importacoes as cegas e passam a decidir com base em evidencias tecnicas visiveis antes de persistir um lote no sistema.

## Definition of Done

- O DQ report renderiza uma tabela expansivel com colunas e amostras consistentes com o contrato ETL.
- Severidade `error` bloqueia commit e severidade `warning` exige override explicito.
- A UI cobre estados de loading, vazio e erro sem deixar caminhos de importacao ambigoo.
- Testes de pagina e hooks provam o gate de severidade antes da liberacao da fase.

## Issues

### ISSUE-F4-02-01 - Renderizar o DQ report em tabela expansivel
Status: todo

**User story**
Como pessoa que revisa um lote ETL, quero ver o DQ report em uma tabela expansivel para entender rapidamente quais checks afetaram quais linhas.

**Plano TDD**
1. `Red`: ampliar `frontend/src/features/leads-import/LeadImportPage.tsx`, `frontend/src/features/leads-import/components/LeadMappingTable.tsx` e `frontend/src/features/leads-import/__tests__/LeadImportPage.validation.test.tsx` para falhar quando o `dq_report` nao for renderizado com as colunas corretas.
2. `Green`: implementar o widget de DQ report com tabela expansivel mostrando `check_name`, `severity`, `affected_rows` e `sample`.
3. `Refactor`: separar a renderizacao do DQ report do restante da tabela de mapeamento para reduzir acoplamento e facilitar evolucao do componente.

**Criterios de aceitacao**
- Given um `dq_report`, When o widget renderiza, Then mostra exatamente `check_name | severity | affected_rows | sample`.
- Given samples disponiveis, When o usuario expande uma linha, Then a amostra fica visivel sem perder o contexto da tabela.

### ISSUE-F4-02-02 - Controlar Importar mesmo assim por severidade
Status: todo

**User story**
Como pessoa que decide se um lote pode prosseguir, quero que o botao de override respeite a severidade dos checks para impedir commits perigosos.

**Plano TDD**
1. `Red`: ampliar `frontend/src/features/leads-import/LeadImportPage.tsx`, `frontend/src/features/leads-import/__tests__/LeadImportPage.validation.test.tsx` e `frontend/src/features/leads-import/hooks/__tests__/useLeadImportWorkflow.test.ts` para falhar quando o gate de severidade nao bloquear `error`.
2. `Green`: implementar a regra de UX em que `error` bloqueia o commit e `warning` libera o botao "Importar mesmo assim", enviando `force_warnings=true`.
3. `Refactor`: centralizar a avaliacao de severidade para manter a regra consistente entre widget, botoes e service layer.

**Criterios de aceitacao**
- Given ao menos um item com `severity=error`, When o usuario tenta prosseguir, Then o commit fica bloqueado.
- Given apenas warnings, When o usuario escolhe override, Then o commit envia `force_warnings=true`.

### ISSUE-F4-02-03 - Cobrir estados vazios, loading e erro do DQ report
Status: todo

**User story**
Como pessoa que usa a UI em condicoes reais, quero feedback claro quando o DQ report ainda esta carregando, falhou ou voltou vazio para nao confirmar uma importacao por engano.

**Plano TDD**
1. `Red`: ampliar `frontend/src/features/leads-import/__tests__/LeadImportPage.validation.test.tsx` e `frontend/src/features/leads-import/hooks/useLeadImportUpload.ts` para falhar quando os estados de loading, vazio ou erro do DQ report nao estiverem cobertos.
2. `Green`: implementar mensagens e bloqueios explicitos para preview em andamento, ausencia de resultados e falha de carregamento do DQ report.
3. `Refactor`: separar estado de carregamento do preview ETL do estado de renderizacao do widget para evitar condicoes inconsistentes na tela.

**Criterios de aceitacao**
- Given preview em andamento, When o DQ ainda nao chegou, Then o estado de loading e explicito e nao permite commit.
- Given erro ao carregar o DQ, When a UI reage, Then o usuario nao consegue confirmar importacao por engano.

## Artifact Minimo do Epico

- `artifacts/phase-f4/epic-f4-02-dq-report-widget.md` com evidencias do widget, gate por severidade e cobertura de estados de UI.

## Dependencias

- [PRD](../PRD-LEAD-ETL-FUSION.md)
- [SCRUM-GOV](../SCRUM-GOV.md)
- [DECISION-PROTOCOL](../DECISION-PROTOCOL.md)
