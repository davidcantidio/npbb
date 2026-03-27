---
doc_id: "ISSUE-F1-01-001-TEMPLATE-USER-STORY-CANONICO"
version: "1.2"
status: "done"
owner: "PM"
last_updated: "2026-03-25"
task_instruction_mode: "required"
decision_refs:
  - "PROJETOS/OPENCLAW-MIGRATION/auditorias/RELATORIO-AUDITORIA-MIGRATION-R01.md#follow-ups-bloqueantes"
---

# ISSUE-F1-01-001 - Template User Story canonico

## User Story

Como agente executor do framework, quero um `TEMPLATE-USER-STORY.md` canonico alinhado a `GOV-USER-STORY.md`, para que toda US criada seja elegivel e consistente com a migracao Feature-first.

## Feature de Origem

- **Feature**: Feature 2 (Templates de Artefato)
- **Comportamento coberto**: Follow-up B1 / ACHADO A-02 — criacao de `PROJETOS/COMUM/TEMPLATE-USER-STORY.md` conforme US 2.2 e Task 2.2.1 do spec.

## Contexto Tecnico

O relatorio R01 constatou ausencia do ficheiro. O spec exige frontmatter (`doc_id`, `version`, `status`, `owner`, `last_updated`, `task_instruction_mode`, `feature_id`, `decision_refs`) e campos obrigatorios da User Story.

## Plano TDD

- Red: nao aplicavel (artefacto Markdown; validacao documental)
- Green: ficheiro criado e referenciavel por SESSION-PLANEJAR e agentes
- Refactor: alinhar redaccao ao `GOV-USER-STORY.md` sem duplicar normas

## Criterios de Aceitacao

- [x] `PROJETOS/COMUM/TEMPLATE-USER-STORY.md` existe
- [x] Frontmatter completo conforme Task 2.2.1 do [openclaw-migration-spec.md](../../../openclaw-migration-spec.md)
- [x] Secoes obrigatorias: User Story (Como/Quero/Para), Feature de Origem, Contexto Tecnico, Criterios G/W/T, DoD, Tasks, Arquivos Envolvidos, Artefato Minimo, Handoff revisao, Dependencias
- [x] Coerente com limites em `PROJETOS/COMUM/GOV-USER-STORY.md`

## Definition of Done da Issue

- [x] `TASK-1.md` executada e evidencias registadas no handoff
- [x] Revisao pos-issue conforme governanca do projeto

## Tasks

- [T1 - Criar TEMPLATE-USER-STORY.md](./TASK-1.md)

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/TEMPLATE-USER-STORY.md` (criar)
- `PROJETOS/COMUM/GOV-USER-STORY.md`
- `PROJETOS/OPENCLAW-MIGRATION/openclaw-migration-spec.md`

## Artifact Minimo

- `TEMPLATE-USER-STORY.md` em COMUM

## Handoff para Revisao Pos-Issue

status: ready
round: 1
base_commit: 25c203f6462d7f7e71dcdcc4029e14ca83549e51
target_commit: d0e7314253ef50ccac7ec502cf286b3b72574166
evidencia: git diff 25c203f6462d7f7e71dcdcc4029e14ca83549e51..d0e7314253ef50ccac7ec502cf286b3b72574166; para README ready_for_review, EPIC e manifesto da fase ver commit seguinte na branch (git log --oneline -2; mensagem contem CLOSE)
commits_execucao:
  - d0e7314253ef50ccac7ec502cf286b3b72574166 OPENCLAW-MIGRATION ISSUE-F1-01-001-TEMPLATE-USER-STORY-CANONICO T1: criar TEMPLATE-USER-STORY.md em COMUM
  - cd2d65da169c32174d633d4610a628960a27522c OPENCLAW-MIGRATION ISSUE-F1-01-001-TEMPLATE-USER-STORY-CANONICO CLOSE: preparar handoff de revisao
validacoes_executadas:
  - rg -n "TEMPLATE-USER-STORY|User Story" PROJETOS/COMUM --glob "*.md" -> pass (template indexado em COMUM)
  - confronto manual Task 2.2.1 (openclaw-migration-spec.md) vs seccoes do template -> pass
  - limites GOV-USER-STORY (max tasks/SP, required) referenciados no template -> pass
arquivos_de_codigo_relevantes:
  - `PROJETOS/COMUM/TEMPLATE-USER-STORY.md`
  - `PROJETOS/OPENCLAW-MIGRATION/F1-REMEDIACAO-HOLD-R01/issues/ISSUE-F1-01-001-TEMPLATE-USER-STORY-CANONICO/TASK-1.md`
limitacoes:
  - Nao existe pasta `sprints/` nem `SPRINT-*.md` em PROJETOS/OPENCLAW-MIGRATION; cascata documental da SESSION-IMPLEMENTAR-ISSUE passo 3.4 sem ficheiro sprint alvo.

## Dependencias

- [Intake](../../../INTAKE-OPENCLAW-MIGRATION.md)
- [PRD](../../../PRD-OPENCLAW-MIGRATION.md)
- [Epic](../../EPIC-F1-01-REMEDIACAO-HOLD-MIGRATION-R01.md)
- [Fase](../../F1_OPENCLAW-MIGRATION_EPICS.md)
- [Relatorio R01](../../../auditorias/RELATORIO-AUDITORIA-MIGRATION-R01.md)
