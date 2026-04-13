---
doc_id: "US-1-02-TELA-UNIFICADA-DE-IMPORTACAO-E-ESTADO-DO-LOTE"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-04-13"
task_instruction_mode: "required"
feature_id: "FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD"
decision_refs: []
---

# US-1-02 - Tela unificada de importacao e estado do lote

## User Story

Como operador interno do NPBB, quero concluir a importacao de leads e consultar
o estado do lote a partir de uma unica tela para nao alternar entre fluxos
separados enquanto acompanho Bronze, Silver, Gold ou ETL.

## Feature de Origem

- **Feature**: FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD
- **Comportamento coberto**: shell canonico em `/leads/importar`, retomada por
  `batch_id` + `step`, fluxo ETL inline e compatibilidade dos deep links
  legados de mapeamento/pipeline.

## Contexto Tecnico

A `US-1-01` fechou os contratos de lote Bronze, mapeamento Silver, pipeline
Gold e ETL de leads, mas a UX ainda estava fragmentada em rotas separadas. O
PRD do projeto pede explicitamente uma tela unificada de importacao e consulta
do estado do lote, reutilizando os endpoints ja existentes sem abrir novo
backend por padrao.

## Plano TDD (opcional no manifesto da US)

- **Red**: explicitar a falha de navegacao fragmentada nos testes de rota e UI
- **Green**: compor o shell canonico com upload, mapeamento, pipeline e ETL
- **Refactor**: manter rotas legadas como redirects finos e centralizar o
  estado do wizard em query params

## Criterios de Aceitacao (Given / When / Then)

- **Given** um operador em `/leads/importar`,
  **when** ele envia um arquivo Bronze e gera o preview,
  **then** o mesmo shell permite seguir para mapeamento e pipeline sem trocar
  manualmente de rota.
- **Given** um operador com `batch_id` e `step` validos,
  **when** ele reabre a rota canonica ou usa um deep link legado,
  **then** o shell retoma a etapa correta e preserva o contexto do lote.
- **Given** um operador no ramo ETL,
  **when** ele gera preview, lida com warnings e confirma o commit,
  **then** o resumo de DQ e o resultado final aparecem no mesmo shell.
- **Given** um lote com metadados e status de pipeline,
  **when** o operador acessa mapeamento ou pipeline dentro do shell,
  **then** arquivo, plataforma, data, stage e `pipeline_status` ficam visiveis
  na experiencia unificada.

## Definition of Done da User Story

- [x] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [x] Criterios Given/When/Then verificados
- [x] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [x] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

- [T1 - Implementar shell canonico e redirects de compatibilidade](./TASK-1.md)
- [T2 - Cobrir o fluxo unificado com testes de rota e estados operacionais](./TASK-2.md)

## Arquivos Reais Envolvidos

- `PROJETOS/NPBB/PRD-NPBB.md`
- `frontend/src/app/AppRoutes.tsx`
- `frontend/src/pages/leads/ImportacaoPage.tsx`
- `frontend/src/pages/leads/MapeamentoPage.tsx`
- `frontend/src/pages/leads/PipelineStatusPage.tsx`
- `frontend/src/pages/leads/LegacyLeadStepRedirect.tsx`
- `frontend/src/pages/__tests__/ImportacaoPage.test.tsx`
- `frontend/src/pages/__tests__/LegacyLeadStepRedirect.test.tsx`

## Artefato Minimo

- `features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD.md`
- `features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/user-stories/US-1-02-TELA-UNIFICADA-DE-IMPORTACAO-E-ESTADO-DO-LOTE/README.md`
- `features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/user-stories/US-1-02-TELA-UNIFICADA-DE-IMPORTACAO-E-ESTADO-DO-LOTE/TASK-1.md`
- `features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/user-stories/US-1-02-TELA-UNIFICADA-DE-IMPORTACAO-E-ESTADO-DO-LOTE/TASK-2.md`

## Handoff para Revisao Pos-User Story

status: pronto_para_revisao
base_commit: b37d9a8f179d5fa8e4d3f3143893ef421ea61a8a
target_commit: worktree
evidencia: |
  - git diff b37d9a8f179d5fa8e4d3f3143893ef421ea61a8a -- frontend/src/pages/leads/ImportacaoPage.tsx frontend/src/pages/leads/MapeamentoPage.tsx frontend/src/pages/leads/PipelineStatusPage.tsx frontend/src/pages/leads/LegacyLeadStepRedirect.tsx frontend/src/pages/__tests__/ImportacaoPage.test.tsx frontend/src/pages/__tests__/LegacyLeadStepRedirect.test.tsx
  - rg -n '"/leads/importar"|"/leads/mapeamento"|"/leads/pipeline"' frontend/src/app/AppRoutes.tsx
  - npm run typecheck
  - npm run test -- ImportacaoPage.test.tsx LegacyLeadStepRedirect.test.tsx MapeamentoPage.test.tsx PipelineStatusPage.test.tsx --run
commits_execucao:
  - worktree local sobre b37d9a8f179d5fa8e4d3f3143893ef421ea61a8a
validacoes_executadas:
  - frontend: `npm run typecheck`
  - frontend: `npm run test -- ImportacaoPage.test.tsx LegacyLeadStepRedirect.test.tsx MapeamentoPage.test.tsx PipelineStatusPage.test.tsx --run` (18 passed)
arquivos_de_codigo_relevantes:
  - frontend/src/app/AppRoutes.tsx
  - frontend/src/pages/leads/ImportacaoPage.tsx
  - frontend/src/pages/leads/MapeamentoPage.tsx
  - frontend/src/pages/leads/PipelineStatusPage.tsx
  - frontend/src/pages/leads/LegacyLeadStepRedirect.tsx
  - frontend/src/pages/__tests__/ImportacaoPage.test.tsx
  - frontend/src/pages/__tests__/LegacyLeadStepRedirect.test.tsx
limitacoes:
  - o ramo ETL nao expoe `batch_id`; o shell mostra preview, warnings e commit inline sem consulta persistente de lote para esse ramo
  - `frontend/src/app/AppRoutes.tsx` contem limpeza local preexistente fora do escopo de leads; revisar as rotas da trilha de leads pelo comando `rg` acima

## Registo de revisao pos-User Story (ROUND 1)

```text
REVISAO POS-USER-STORY
─────────────────────────────────────────
User Story: US-1-02-TELA-UNIFICADA-DE-IMPORTACAO-E-ESTADO-DO-LOTE
Status antes: ready_for_review
Objetivo: shell unificado /leads/importar, retomada batch_id+step, ETL inline, redirects legados
task_instruction_mode: required
ROUND: 1
Feature/PRD auditados: FEATURE-1, PRD-NPBB (tela unificada sem novo backend por padrao)
BASE_COMMIT: b37d9a8f179d5fa8e4d3f3143893ef421ea61a8a
TARGET_COMMIT: worktree
Evidencias: handoff acima + confirmacao de rotas em AppRoutes.tsx; pipeline via POST /leads/batches/{id}/executar-pipeline em leads_import.ts
Limitacoes da revisao: diff de AppRoutes.tsx fora da trilha leads excluido do juizo de escopo; ramo ETL sem batch_id conforme handoff
Risco de expandir escopo: baixo (lacuna ETL documentada, fora do fecho desta US)
SCOPE-LEARN presente: nao
modo: padrao
DRIFT_INDICE: nenhuma para Markdown; preflight ../fabrica/bin/ensure-fabrica-projects-index-runtime.sh nao executado (artefacto ausente neste workspace); scripts/framework_governance/validate_us_traceability.py ausente no repositório — revisao baseada em manifesto, evidencia git e leitura de codigo + typecheck local (exit 0)
─────────────────────────────────────────
VEREDITO PROPOSTO
veredito: aprovada
status_resultante_user_story: done
destino_proposto: nenhum
Alinhamento G/W/T: fluxo Bronze no mesmo shell; retomada e deep links via LegacyLeadStepRedirect; ETL preview/warnings/commit no shell; resumo de lote (BatchSummaryCard) com metadados e pipeline_status; criterio de retomada com batch_id+step aplica-se ao fluxo com lote (limitacao ETL explicita no handoff, coerente com T1 stop_conditions)
─────────────────────────────────────────
```

## Dependencias

- [Feature piloto](../../FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD.md)
- [PRD do projeto](../../../../PRD-NPBB.md)
- [US-1-01](../US-1-01-INGESTAO-E-MAPEAMENTO-INICIAL/README.md)
- [GOV-USER-STORY.md](../../../../COMUM/GOV-USER-STORY.md)

## Navegacao Rapida

- [TASK-1](TASK-1.md)
- [TASK-2](TASK-2.md)
