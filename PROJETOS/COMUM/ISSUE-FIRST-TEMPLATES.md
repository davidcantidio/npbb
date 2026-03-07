---
doc_id: "ISSUE-FIRST-TEMPLATES.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-07"
---

# ISSUE-FIRST-TEMPLATES

## Objetivo

Definir a estrutura canonica para novos projetos em `PROJETOS/` no modelo `issue-first`, em que o trabalho detalhado vive em arquivos proprios de issue e a sprint permanece apenas como manifesto de selecao.

## Estrutura Canonica

```text
PROJETOS/<PROJETO>/
  PRD-<PROJETO>.md
  DECISION-PROTOCOL.md
  feito/
  F1-<NOME-DA-FASE>/
    F1_<PROJETO>_EPICS.md
    EPIC-F1-01-<NOME>.md
    issues/
      ISSUE-F1-01-001-<NOME>.md
      ISSUE-F1-01-002-<NOME>.md
    sprints/
      SPRINT-F1-01.md
```

## Responsabilidades por Documento

- `F<N>_<PROJETO>_EPICS.md`: objetivo da fase, gate, escopo, tabela de epicos e dependencias entre epicos
- `EPIC-*.md`: manifesto do epico, DoD do epico, dependencias, artifact minimo e indice das issues
- `issues/ISSUE-*.md`: user story, plano TDD, criterios `Given/When/Then`, DoD da issue, tarefas decupadas e artefatos
- `sprints/SPRINT-*.md`: selecao de issues, capacidade, riscos e consolidacao de status

## Template de `EPIC-*.md`

```markdown
---
doc_id: "EPIC-F1-01-NOME-DO-EPICO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "YYYY-MM-DD"
---

# EPIC-F1-01 - Nome do Epico

## Objetivo

## Resultado de Negocio Mensuravel

## Contexto Arquitetural

## Definition of Done do Epico
- [ ]

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-01-001 | Nome da issue | Resultado tecnico unico | 3 | todo | [ISSUE-F1-01-001-NOME.md](./issues/ISSUE-F1-01-001-NOME.md) |

## Artifact Minimo do Epico

## Dependencias
- [PRD](../PRD-PROJETO.md)
- [Fase](./F1_PROJETO_EPICS.md)
- [Decision Protocol](../DECISION-PROTOCOL.md)

## Navegacao Rapida
- `[[./issues/ISSUE-F1-01-001-NOME]]`
- `[[../PRD-PROJETO]]`
```

## Template de `issues/ISSUE-*.md`

```markdown
---
doc_id: "ISSUE-F1-01-001-NOME.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "YYYY-MM-DD"
---

# ISSUE-F1-01-001 - Nome da Issue

## User Story
Como <papel>, quero <acao> para <resultado>.

## Contexto Tecnico

## Plano TDD
- Red:
- Green:
- Refactor:

## Criterios de Aceitacao
- Given ..., When ..., Then ...
- Given ..., When ..., Then ...

## Definition of Done da Issue
- [ ]

## Tarefas Decupadas
- [ ] T1:
- [ ] T2:
- [ ] T3:

## Arquivos Reais Envolvidos
- `backend/...`
- `frontend/...`

## Artifact Minimo
- `artifacts/...`

## Dependencias
- [Epic](../EPIC-F1-01-NOME-DO-EPICO.md)
- [Fase](../F1_PROJETO_EPICS.md)
- [PRD](../../PRD-PROJETO.md)

## Navegacao Rapida
- `[[../EPIC-F1-01-NOME-DO-EPICO]]`
- `[[../../PRD-PROJETO]]`
```

## Template de `sprints/SPRINT-*.md`

```markdown
---
doc_id: "SPRINT-F1-01.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "YYYY-MM-DD"
---

# SPRINT-F1-01

## Objetivo da Sprint

## Capacidade
- story_points_planejados:
- issues_planejadas:
- override:

## Issues Selecionadas

| Issue ID | Nome | SP | Status | Documento |
|---|---|---|---|---|
| ISSUE-F1-01-001 | Nome da issue | 3 | todo | [ISSUE-F1-01-001-NOME.md](../issues/ISSUE-F1-01-001-NOME.md) |

## Riscos e Bloqueios

## Encerramento
- decisao:
- observacoes:

## Navegacao Rapida
- `[[../issues/ISSUE-F1-01-001-NOME]]`
- `[[../EPIC-F1-01-NOME-DO-EPICO]]`
```

## Convencao de Links

- link Markdown relativo e a referencia canonica
- wikilink e complementar e nunca deve ser o unico meio de navegacao
- usar wikilinks qualificados por caminho local para evitar ambiguidade
- evitar wikilinks curtos como `[[EPICS]]`, `[[DECISION-PROTOCOL]]` ou `[[EPIC-F1-01]]`
- preferir:
  - `[[./issues/ISSUE-F1-01-001-NOME]]`
  - `[[../EPIC-F1-01-NOME-DO-EPICO]]`
  - `[[../../PRD-PROJETO]]`

## Regras de Adocao

- aplicar este padrao apenas a projetos novos
- nao migrar automaticamente projetos ativos ou o historico em `FEITO/`
- quando um projeto legado nao usar `issues/`, a issue pode permanecer embutida no epico ate decisao formal de migracao
