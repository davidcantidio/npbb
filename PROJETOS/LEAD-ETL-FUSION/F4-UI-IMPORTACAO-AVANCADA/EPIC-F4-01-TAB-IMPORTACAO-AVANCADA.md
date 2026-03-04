---
doc_id: "EPIC-F4-01-TAB-IMPORTACAO-AVANCADA"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# EPIC-F4-01 - Tab Importacao Avancada

## Objetivo

Adicionar uma tab "Importacao avancada" em `/leads` que consome `POST /leads/import/etl/preview` e `POST /leads/import/etl/commit`, coexistindo com o fluxo legado de importacao.

## Resultado de Negocio Mensuravel

Usuarios conseguem importar arquivos fora do padrao a partir da mesma tela de leads, sem abandonar a interface atual nem executar processos manuais fora da aplicacao.

## Definition of Done

- `/leads` passa a ter uma tab dedicada ao fluxo ETL avancado.
- O fluxo legado continua sendo a experiencia padrao e permanece funcional.
- O service layer do frontend passa a armazenar `session_token` e dados do preview ETL.
- O commit ETL reutiliza a sessao aprovada sem interferir no importador antigo.

## Issues

### ISSUE-F4-01-01 - Introduzir a aba Importacao avancada em /leads
Status: todo

**User story**
Como pessoa que importa leads em `/leads`, quero uma aba dedicada ao fluxo avancado para revisar arquivos fora do padrao sem perder o acesso ao fluxo tradicional.

**Plano TDD**
1. `Red`: ampliar `frontend/src/features/leads-import/LeadImportPage.tsx` e `frontend/src/features/leads-import/__tests__/LeadImportPage.validation.test.tsx` para falhar quando a pagina nao renderizar uma aba nova preservando o fluxo atual.
2. `Green`: adicionar a tab "Importacao avancada" em `/leads`, com separacao clara entre o fluxo legado e o fluxo ETL.
3. `Refactor`: consolidar estado de navegacao da pagina para que a escolha de tab nao replique logica de upload, erros ou listagem de leads.

**Criterios de aceitacao**
- Given acesso a pagina `/leads`, When o usuario entra, Then ve uma nova aba sem perder o fluxo atual.
- Given nao houve escolha explicita do usuario, When a pagina abre, Then o tab padrao continua sendo o fluxo legado para minimizar regressao.

### ISSUE-F4-01-02 - Consumir preview ETL com session_token no service layer
Status: todo

**User story**
Como pessoa que revisa um preview ETL, quero que o frontend retenha o `session_token` e o DQ report para prosseguir ao commit sem recalcular o lote.

**Plano TDD**
1. `Red`: ampliar `frontend/src/services/leads_import.ts`, `frontend/src/features/leads-import/hooks/useLeadImportUpload.ts` e `frontend/src/features/leads-import/hooks/__tests__/useLeadImportWorkflow.test.ts` para falhar quando o estado do preview ETL nao reter `session_token` e `dq_report`.
2. `Green`: introduzir `previewLeadImportEtl` no service layer e adaptar o hook de upload para armazenar o contrato ETL sem colidir com o preview legado.
3. `Refactor`: separar os tipos do preview legado e do preview ETL para evitar condicionais difusas no estado da pagina.

**Criterios de aceitacao**
- Given upload na aba avancada, When o preview retorna, Then o frontend armazena `session_token` e `dq_report`.
- Given falha de preview, When o erro chega, Then o estado nao deixa commit residual habilitado.

### ISSUE-F4-01-03 - Executar commit ETL sem quebrar o fluxo legado
Status: todo

**User story**
Como pessoa que aprova o preview avancado, quero executar o commit ETL a partir da mesma pagina para concluir a importacao sem interferir no fluxo tradicional.

**Plano TDD**
1. `Red`: ampliar `frontend/src/features/leads-import/LeadImportPage.tsx`, `frontend/src/features/leads-import/components/LeadImportSummaryDialog.tsx` e `frontend/src/features/leads-import/hooks/useLeadImportWorkflow.ts` para falhar quando o commit ETL usar o endpoint errado ou quebrar o fluxo legado.
2. `Green`: introduzir `commitLeadImportEtl` no service layer e conectar a confirmacao da aba avancada ao endpoint ETL usando o token da sessao aprovada.
3. `Refactor`: isolar o estado de commit da aba avancada para que erros, retries e resumo final nao contaminem o fluxo legado.

**Criterios de aceitacao**
- Given preview avancado valido, When o usuario confirma o commit, Then o frontend chama o endpoint ETL com o token da sessao.
- Given uso do import legado, When a aba antiga e usada, Then ela continua chamando apenas os endpoints antigos.

## Artifact Minimo do Epico

- `artifacts/phase-f4/epic-f4-01-tab-importacao-avancada.md` com evidencias da navegacao por tabs, preview ETL e commit isolado do fluxo legado.

## Dependencias

- [PRD](../PRD-LEAD-ETL-FUSION.md)
- [SCRUM-GOV](../SCRUM-GOV.md)
- [DECISION-PROTOCOL](../DECISION-PROTOCOL.md)
