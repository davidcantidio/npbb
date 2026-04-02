---
doc_id: "GOV-USER-STORY.md"
version: "1.4"
status: "active"
owner: "PM"
last_updated: "2026-03-30"
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
- US com dependencia de outra US que ainda nao esteja `done` ou `cancelled`
  nao e elegivel para execucao
- `ready_for_review` nao satisfaz dependencia entre user stories; esse estado
  fecha apenas a execucao local e aguarda revisao
- o agente executor deve responder `BLOQUEADO` em vez de improvisar

## Ciclo de gate da User Story

- ciclo canonico: `execucao -> ready_for_review -> revisao -> done`
- `ready_for_review` representa implementacao concluida com handoff persistido,
  mas ainda nao encerra a user story
- so `done` ou `cancelled` liberam a proxima user story dependente

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

## Gate anti-drift: promover `TASK-N.md` a `done`

Antes de gravar `status: done` numa task granularizada:

- os paths em `write_scope` devem refletir ficheiros **realmente** alterados ou
  validados na execucao (ou a task deve ser `cancelled` com justificativa)
- quando `testes_ou_validacoes_obrigatorias` ou `testes_red` citarem comandos ou
  ficheiros de teste, o executor deve ter corrido essas validacoes com resultado
  coerente antes do `done`, salvo excecao documentada na propria task
- **nao** deixar `todo` no manifesto da task quando o codigo ou os artefatos
  descritos ja existem no repositorio sem fecho documental; alinhar estado ou
  abrir task corretiva explicita

Detalhe de campos por task: `SPEC-TASK-INSTRUCTIONS.md` e `GOV-COMMIT-POR-TASK.md`.

Edicao de `README.md`, `TASK-*.md` e `REV-US-*.md` em caso de patches dificeis:
`PROJETOS/COMUM/SPEC-EDITOR-ARTEFACTOS.md`.

## Artefatos suplementares na pasta da User Story

- `SCOPE-LEARN.md` (opcional): aprendizado emergente sobre lacunas nos criterios
  `Given/When/Then` face a evidencia de execucao; formato em
  `TEMPLATE-SCOPE-LEARN.md`. O executor nao altera criterios no manifesto sem
  veredito do agente senior conforme `SESSION-REVISAR-US.md`.
