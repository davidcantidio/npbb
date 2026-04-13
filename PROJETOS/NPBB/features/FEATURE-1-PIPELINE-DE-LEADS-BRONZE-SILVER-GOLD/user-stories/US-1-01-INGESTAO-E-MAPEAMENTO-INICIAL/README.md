---
doc_id: "US-1-01-INGESTAO-E-MAPEAMENTO-INICIAL"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-04-13"
task_instruction_mode: "required"
feature_id: "FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD"
decision_refs: []
---

# US-1-01 - Ingestao e mapeamento inicial do lote

## User Story

Como operador interno do NPBB, quero enviar um arquivo de leads, registrar os
metadados do lote e concluir o mapeamento inicial para que o pipeline Gold
possa ser executado com rastreabilidade.

## Feature de Origem

- **Feature**: FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD
- **Comportamento coberto**: ingestao do lote piloto, persistencia Bronze e
  configuracao minima do estado Silver.

## Contexto Tecnico

A feature reaproveita o contexto legado de `NPBB-LEADS`, mas agora sob o layout
canônico `Feature -> User Story -> Task`. A primeira US deve cobrir os pontos
minimos para tornar o lote auditavel antes da promocao para Gold.

## Plano TDD (opcional no manifesto da US)

- **Red**: cobrir ausencia de persistencia do lote e de metadados obrigatorios
- **Green**: introduzir fluxo minimo para upload, metadados e mapeamento inicial
- **Refactor**: consolidar nomes de campos e pontos de extensao para as USs seguintes

## Criterios de Aceitacao (Given / When / Then)

- **Given** um operador com arquivo CSV ou XLSX valido,
  **when** ele inicia a importacao,
  **then** o sistema cria um lote Bronze com arquivo bruto e metadados de envio.
- **Given** um lote Bronze criado,
  **when** o operador conclui o mapeamento minimo das colunas e associa o evento,
  **then** o estado Silver fica persistido e rastreavel por lote e linha.
- **Given** a US em revisao,
  **when** a documentacao do projeto for inspecionada,
  **then** os artefatos e wrappers locais continuam usando apenas o paradigma atual.

## Definition of Done da User Story

- [x] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [x] Criterios Given/When/Then verificados
- [x] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [x] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

- [T1 - Estruturar lote Bronze e mapeamento Silver inicial](./TASK-1.md)

## Arquivos Reais Envolvidos

- `INTAKE-NPBB.md`
- `PRD-NPBB.md`
- `AUDIT-LOG.md`
- `backend/`
- `frontend/`
- `lead_pipeline/`
- `features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD.md`

## Artefato Minimo

- `features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD.md`
- `features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/user-stories/US-1-01-INGESTAO-E-MAPEAMENTO-INICIAL/README.md`
- `features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/user-stories/US-1-01-INGESTAO-E-MAPEAMENTO-INICIAL/TASK-1.md`

## Handoff para Revisao Pos-User Story

status: pronto_para_revisao
base_commit: d5e61da4e04878735538fcffcb37aafb6847e74f
target_commit: 532e9031111aaa54a18017e80acb298a1cb97402
evidencia: |
  - git diff d5e61da4e04878735538fcffcb37aafb6847e74f..532e9031111aaa54a18017e80acb298a1cb97402 -- backend/app/models/lead_batch.py backend/app/schemas/lead_batch.py backend/app/routers/leads.py frontend/src/pages/leads/ImportacaoPage.tsx frontend/src/services/leads_import.ts docs/leads_importacao.md
  - Lote Bronze criado via POST /leads/batches com arquivo bruto, metadados (plataforma, data, usuario) e stage=bronze.
  - Mapeamento Silver via POST /leads/batches/{id}/mapear persiste linhas em leads_silver com evento_id e dados_brutos JSON.
  - Pipeline Gold via POST /leads/batches/{id}/executar-pipeline promove dados do Silver para a tabela lead canonica.
  - Fluxo ETL alternativo (POST /leads/import/etl/preview + commit) com DQ report, strict/force_warnings e idempotencia.
commits_execucao:
  - 2fb69c54d24fb320c167669e27ba249e13b0f5b9
  - bda4c1dd839161dd62c0356d612e3ca66e0f1494
  - 34cfba8b6c40d3d2981be66f1108631008fdb217
  - e5fe7189d945a33aa9ebdabff7a3adfa1f33c096
  - 532e9031111aaa54a18017e80acb298a1cb97402
validacoes_executadas:
  - revisao documental do handoff alinhada a `PROJETOS/NPBB/SESSION-REVISAR-US.md`
  - evidencia reproduzivel consolidada no range historico `d5e61da4..532e9031`
  - docs do fluxo ETL e do lote piloto mantidas em `docs/leads_importacao.md`
  - observacao: `backend/tests/test_leads_import_etl_usecases.py` possui falhas preexistentes registradas em `AGENTS.md` e nao foi usado como gate local nesta sessao
arquivos_de_codigo_relevantes:
  - backend/app/models/lead_batch.py
  - backend/app/schemas/lead_batch.py
  - backend/app/routers/leads.py
  - backend/app/modules/leads_publicidade/application/etl_import/
  - frontend/src/pages/leads/ImportacaoPage.tsx
  - frontend/src/services/leads_import.ts
limitacoes:
  - A UI oferece dois fluxos (Bronze+mapeamento e ETL); unificacao visual fica para US seguinte.

## Resultado da Revisao Pos-User-Story

- veredito: `aprovada`
- status_resultante_user_story: `done`
- evidencia_revisada: `git diff d5e61da4e04878735538fcffcb37aafb6847e74f..532e9031111aaa54a18017e80acb298a1cb97402 -- backend/app/models/lead_batch.py backend/app/schemas/lead_batch.py backend/app/routers/leads.py frontend/src/pages/leads/ImportacaoPage.tsx frontend/src/services/leads_import.ts docs/leads_importacao.md`
- observacoes:
  - a rastreabilidade de Bronze, Silver, pipeline Gold e ETL ficou coberta pela serie historica de commits da entrega original
  - a unificacao visual da UX e a compatibilidade de deep links seguem para `US-1-02`

## Dependencias

- [Feature piloto](../../FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD.md)
- [PRD do projeto](../../../../PRD-NPBB.md)
- Outras USs: nenhuma
- [GOV-USER-STORY.md](../../../../COMUM/GOV-USER-STORY.md)

## Navegacao Rapida

- [TASK-1](TASK-1.md)
