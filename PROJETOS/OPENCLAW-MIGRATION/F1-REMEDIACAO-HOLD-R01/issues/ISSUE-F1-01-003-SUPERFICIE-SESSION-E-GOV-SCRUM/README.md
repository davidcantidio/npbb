---
doc_id: "ISSUE-F1-01-003-SUPERFICIE-SESSION-E-GOV-SCRUM"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-25"
task_instruction_mode: "required"
decision_refs:
  - "PROJETOS/OPENCLAW-MIGRATION/auditorias/RELATORIO-AUDITORIA-MIGRATION-R01.md#follow-ups-bloqueantes"
---

# ISSUE-F1-01-003 - Superficie SESSION e GOV-SCRUM

## User Story

Como operador do framework, quero SESSIONs e `GOV-SCRUM.md` consistentes com Feature/US/Task e prompts legados depreciados, para que o mapa de sessoes e a governanca operacional nao contradigam o PRD da migracao.

## Feature de Origem

- **Feature**: Feature 1 e Feature 3 (transversal)
- **Comportamento coberto**: Follow-up B3 / ACHADOS A-03, A-05, A-06 e verificacao cruzada `SESSION-IMPLEMENTAR-US` vs `GOV-USER-STORY`.

## Contexto Tecnico

Inclui criacao de `SESSION-REVISAR-US.md`, correcao de `SESSION-MAPA.md` (referencia a ficheiro inexistente), actualizacao de `SESSION-AUDITAR-FEATURE.md` (bloco que reintroduz ISSUE legado), limpeza de termos legados em `GOV-SCRUM.md`, depreciacao explicita de `SESSION-IMPLEMENTAR-ISSUE.md`, `SESSION-AUDITAR-FASE.md`, `SESSION-REVISAR-ISSUE.md`, e ponteiro normativo a `GOV-USER-STORY.md` em `SESSION-IMPLEMENTAR-US.md`.

## Plano TDD

- Red: nao aplicavel
- Green: superficie SESSION e GOV-SCRUM alinhados ao relatorio R01
- Refactor: reduzir duplicacao entre SESSIONs

## Criterios de Aceitacao

- [x] `SESSION-REVISAR-US.md` existe e segue padrao dos demais SESSION-COMUM
- [x] `SESSION-MAPA.md` lista apenas prompts activos coerentes; entradas inexistentes removidas ou corrigidas
- [x] `SESSION-AUDITAR-FEATURE.md` nao manda regressao a fluxos ISSUE nos bloqueios de follow-up
- [x] `SESSION-IMPLEMENTAR-US.md` referencia explicitamente `GOV-USER-STORY.md` para limites de tamanho
- [x] `GOV-SCRUM.md` sem termos legados fora de secao `deprecated` onde ainda necessario
- [x] Tres SESSIONs legados marcados `status: deprecated` com ponteiro ao substituto

## Definition of Done da Issue

- [x] Tasks T1-T6 concluidas em ordem ou com dependencias explicitas registadas
- [x] Revisao pos-issue conforme governanca

## Tasks

- [x] [T1 - Criar SESSION-REVISAR-US.md](./TASK-1.md)
- [x] [T2 - Corrigir SESSION-MAPA.md](./TASK-2.md)
- [x] [T3 - Corrigir SESSION-AUDITAR-FEATURE.md](./TASK-3.md)
- [x] [T4 - Alinhar SESSION-IMPLEMENTAR-US a GOV-USER-STORY](./TASK-4.md)
- [x] [T5 - Atualizar GOV-SCRUM.md](./TASK-5.md)
- [x] [T6 - Depreciar SESSIONs legados](./TASK-6.md)

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/SESSION-REVISAR-US.md` (criar)
- `PROJETOS/COMUM/SESSION-MAPA.md`
- `PROJETOS/COMUM/SESSION-AUDITAR-FEATURE.md`
- `PROJETOS/COMUM/SESSION-IMPLEMENTAR-US.md`
- `PROJETOS/COMUM/GOV-SCRUM.md`
- `PROJETOS/COMUM/SESSION-IMPLEMENTAR-ISSUE.md`
- `PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`
- `PROJETOS/COMUM/SESSION-REVISAR-ISSUE.md`
- `PROJETOS/COMUM/GOV-USER-STORY.md`

## Artifact Minimo

- SESSIONs e GOV-SCRUM actualizados conforme criterios

## Handoff para Revisao Pos-Issue

status: pronto_para_revisao
round: 1
base_commit: 106c221f4cbc1334c274125a68932d80c365970b
target_commit: af8b1c37399ecee31224c5d55aa4ade8a2baea5c
evidencia: git show af8b1c37399ecee31224c5d55aa4ade8a2baea5c
commits_execucao:
  - af8b1c37399ecee31224c5d55aa4ade8a2baea5c
validacoes_executadas:
  - "rg -n \"status:\" nos tres SESSION legados COMUM — frontmatter status: deprecated confirmado"
arquivos_de_codigo_relevantes:
  - PROJETOS/COMUM/SESSION-IMPLEMENTAR-ISSUE.md
  - PROJETOS/COMUM/SESSION-AUDITAR-FASE.md
  - PROJETOS/COMUM/SESSION-REVISAR-ISSUE.md
  - PROJETOS/COMUM/SESSION-MAPA.md
limitacoes: nenhuma

## Dependencias

- [Intake](../../../INTAKE-OPENCLAW-MIGRATION.md)
- [PRD](../../../PRD-OPENCLAW-MIGRATION.md)
- [Epic](../../EPIC-F1-01-REMEDIACAO-HOLD-MIGRATION-R01.md)
- [Fase](../../F1_OPENCLAW-MIGRATION_EPICS.md)
- [Relatorio R01](../../../auditorias/RELATORIO-AUDITORIA-MIGRATION-R01.md)
