---
doc_id: "GOV-USER-STORY.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-25"
---

# GOV-USER-STORY

## Objetivo

Definir a `User Story` como a menor unidade documental completa de execucao
dentro de uma `Feature`, com `Tasks` como filhos executaveis.

## Limites Canonicos

```yaml
max_tasks_por_user_story: 5
max_story_points_por_user_story: 5
max_user_stories_por_feature: sem limite fixo
criterio_de_tamanho: executavel em uma unica sessao de agente sem ambiguidade
```

## Criterio de Elegibilidade para Execucao

- US com `task_instruction_mode: required` sem tasks detalhadas nao e elegivel
  para execucao
- US com dependencia de outra US que ainda nao esteja `done` nao e elegivel
  para execucao
- o agente executor deve responder `BLOQUEADO` em vez de improvisar

## Quando required e obrigatorio

Use `task_instruction_mode: required` quando a User Story contiver qualquer um
destes fatores:

- migration ou mudanca com persistencia/rollback sensivel
- ordem de execucao critica entre tasks
- alteracao multi-camada ou multi-arquivo com dependencia forte
- remediacao originada de auditoria de feature `hold`
- remediacao originada de review de User Story com risco alto ou regressao
  delicada
- handoff planejado para outra IA ou outra sessao

Se nenhum desses fatores existir, `task_instruction_mode: optional` e o
recomendado.

Este documento governa tamanho e elegibilidade da US. Campos minimos por task,
`testes_red` e formato detalhado continuam em `SPEC-TASK-INSTRUCTIONS.md`.

## Artefatos suplementares na pasta da User Story

- `SCOPE-LEARN.md` (opcional): aprendizado emergente sobre lacunas nos criterios
  `Given/When/Then` face a evidencia de execucao; formato em
  `TEMPLATE-SCOPE-LEARN.md`. O executor nao altera criterios no manifesto sem
  veredito do agente senior conforme `SESSION-REVISAR-US.md`.
