---
doc_id: "TEMPLATE-USER-STORY.md"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "YYYY-MM-DD"
task_instruction_mode: "optional"
# feature_id: mesmo valor que feature_key do manifesto (ex. FEATURE-1), nao o nome da pasta completa — ver GOV-FEATURE.md
feature_id: "FEATURE-<N>"
decision_refs: []
---

# US-<PROJETO>-F<N>-<NN> - <titulo curto da User Story>

> Copie este ficheiro para a pasta da feature ou local definido pelo projeto.
> Limites canonicos de tamanho e elegibilidade: `PROJETOS/COMUM/GOV-USER-STORY.md`
> (ex.: `max_tasks_por_user_story`, `max_story_points_por_user_story`, regra de `required`).

## User Story

**Como** <papel ou agente>,
**quero** <acao ou entrega>,
**para** <resultado mensuravel ou criterio de sucesso>.

## Feature de Origem

- **Feature**: <Feature N (titulo no PRD)>
- **Comportamento coberto**: <recorte desta US dentro da feature>

## Contexto Tecnico

<stack, restricoes, dependencias tecnicas, ligacoes a spec ou ADRs>

## Plano TDD (opcional no manifesto da US)

> Quando o trabalho for apenas documental, indique `nao aplicavel` e detalhe TDD em `TASK-N.md` com `tdd_aplicavel: true` quando couber.

- **Red**:
- **Green**:
- **Refactor**:

## Criterios de Aceitacao (Given / When / Then)

- **Given** <precondicao>,
  **when** <acao ou evento>,
  **then** <resultado observavel>.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

Desdobre em ate **5** tasks por US (`GOV-USER-STORY.md`). Com `task_instruction_mode: required`, cada task deve ter ficheiro proprio `TASK-N.md` seguindo `PROJETOS/COMUM/TEMPLATE-TASK.md` e declarando `user_story_id`, `depends_on`, `parallel_safe` e `write_scope`.

Opcional: cabecalhos de sessao `imp-<N>.md` por task — `PROJETOS/COMUM/TEMPLATE-IMP-SESSAO.md`
e parametros em `PROJETOS/COMUM/SESSION-IMPLEMENTAR-US.md`.

- [T1 - <titulo>](./TASK-1.md)
- [T2 - <titulo>](./TASK-2.md)

## Arquivos Reais Envolvidos

- <caminho/relativo/ao/repo>

## Artefato Minimo

- <descricao do entregavel minimo ou caminho>

## Handoff para Revisao

> Preencher ao concluir a execucao da US, antes da revisao senior, seguindo
> `GOV-SCRUM.md` e `SESSION-REVISAR-US.md`.

status: nao_iniciado
base_commit: nao_informado
target_commit: nao_informado
evidencia: nao_informado
commits_execucao: []
validacoes_executadas: []
arquivos_de_codigo_relevantes: []
limitacoes: []

## Dependencias

- [PRD do projeto](../<PROJETO>/PRD-<PROJETO>.md) *(ajustar caminho relativo)*
- Outras USs: <nenhuma | US-X depende de US-Y `done`>
- Tasks internas: usar `depends_on` no frontmatter de `TASK-*.md`
- [GOV-USER-STORY.md](./GOV-USER-STORY.md)
