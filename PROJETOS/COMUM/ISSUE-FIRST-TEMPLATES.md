---
doc_id: "ISSUE-FIRST-TEMPLATES.md"
version: "1.3"
status: "active"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-FIRST-TEMPLATES

## Objetivo

Definir a estrutura canonica para projetos ativos em `PROJETOS/`, em que o trabalho detalhado vive em arquivos proprios de issue, a sprint permanece apenas como manifesto de selecao, o intake antecede o PRD e a auditoria fecha a fase.

## Estrutura Canonica

```text
PROJETOS/<PROJETO>/
  INTAKE-<PROJETO>.md
  PRD-<PROJETO>.md
  DECISION-PROTOCOL.md
  AUDIT-LOG.md
  feito/
  F1-<NOME-DA-FASE>/
    F1_<PROJETO>_EPICS.md
    EPIC-F1-01-<NOME>.md
    issues/
      ISSUE-F1-01-001-<NOME>.md
      ISSUE-F1-01-002-<NOME>.md
    sprints/
      SPRINT-F1-01.md
    auditorias/
      RELATORIO-AUDITORIA-F1-R01.md
```

Intakes adicionais de remediacao podem coexistir na raiz no formato `INTAKE-<PROJETO>-<SLUG>.md`.

## Responsabilidades por Documento

- `INTAKE-*.md`: intake estruturado, taxonomias, restricoes, riscos, rastreabilidade, lacunas conhecidas e checklist de prontidao para PRD
- `PRD-*.md`: objetivo, arquitetura, requisitos, fases e restricoes do projeto
- `AUDIT-LOG.md`: historico cumulativo das rodadas de auditoria e follow-ups
- `F<N>_<PROJETO>_EPICS.md`: objetivo da fase, gate, tabela de epicos, dependencias entre epicos e estado do gate de auditoria
- `EPIC-*.md`: manifesto do epico, DoD do epico, dependencias, artefato minimo e indice das issues
- `issues/ISSUE-*.md`: user story, plano TDD, criterios `Given/When/Then`, DoD da issue, tasks, instructions por task quando exigidas e artefatos
- `sprints/SPRINT-*.md`: selecao de issues, capacidade, riscos e consolidacao de status
- `auditorias/RELATORIO-AUDITORIA-*.md`: evidencia formal do gate da fase

## Template de `INTAKE-*.md`

Usar o modelo oficial em `PROJETOS/COMUM/INTAKE-TEMPLATE.md`.

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
- [Intake](../INTAKE-PROJETO.md)
- [PRD](../PRD-PROJETO.md)
- [Fase](./F1_PROJETO_EPICS.md)
- [Decision Protocol](../DECISION-PROTOCOL.md)
```

## Template de `issues/ISSUE-*.md`

```markdown
---
doc_id: "ISSUE-F1-01-001-NOME.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "YYYY-MM-DD"
task_instruction_mode: "optional"
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

## Definition of Done da Issue
- [ ]

## Tasks Decupadas
- [ ] T1:

## Instructions por Task
> Preencher esta secao apenas quando `task_instruction_mode: required`.

### T1
- objetivo:
- precondicoes:
- arquivos_a_ler_ou_tocar:
  - `frontend/...`
- passos_atomicos:
  1. ...
- comandos_permitidos:
  - `npm run test -- --run`
- resultado_esperado:
- testes_ou_validacoes_obrigatorias:
  - `frontend/...`
- stop_conditions:
  - parar e reportar bloqueio se ...

## Arquivos Reais Envolvidos
- `backend/...`
- `frontend/...`

## Artifact Minimo
- `artifacts/...`

## Dependencias
- [Intake](../../INTAKE-PROJETO.md)
- [Epic](../EPIC-F1-01-NOME-DO-EPICO.md)
- [Fase](../F1_PROJETO_EPICS.md)
- [PRD](../../PRD-PROJETO.md)
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
```

## Template de `AUDIT-LOG.md`

Usar o modelo oficial em `PROJETOS/COMUM/AUDITORIA-LOG-TEMPLATE.md`.

## Template de `auditorias/RELATORIO-AUDITORIA-*.md`

Usar o modelo oficial em `PROJETOS/COMUM/AUDITORIA-REPORT-TEMPLATE.md`.

## Regras de `task_instruction_mode`

- `optional`: tasks podem permanecer apenas como checklist curto
- `required`: cada task deve ter bloco proprio em `## Instructions por Task`
- usar `required` para tasks de alto risco conforme `PROJETOS/COMUM/TASK_INSTRUCTIONS_SPEC.md`
- para compatibilidade de rollout, issues antigas podem nao ter o campo; novas issues devem declarar o modo explicitamente

## Convencao de Links

- link Markdown relativo e a referencia canonica
- wikilink e complementar e nunca deve ser o unico meio de navegacao
- usar wikilinks qualificados por caminho local para evitar ambiguidade
