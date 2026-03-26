---
doc_id: "US-1-01-INGESTAO-E-MAPEAMENTO-INICIAL"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
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

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

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

status: nao_iniciado
base_commit: nao_informado
target_commit: nao_informado
evidencia: nao_informado
commits_execucao: []
validacoes_executadas: []
arquivos_de_codigo_relevantes: []
limitacoes: []

## Dependencias

- [Feature piloto](../../FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD.md)
- [PRD do projeto](../../../../PRD-NPBB.md)
- Outras USs: nenhuma
- [GOV-USER-STORY.md](../../../../COMUM/GOV-USER-STORY.md)

## Navegacao Rapida

- [TASK-1](TASK-1.md)
