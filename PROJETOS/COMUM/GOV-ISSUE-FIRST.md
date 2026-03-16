---
doc_id: "GOV-ISSUE-FIRST.md"
version: "2.3"
status: "active"
owner: "PM"
last_updated: "2026-03-16"
---

# GOV-ISSUE-FIRST

## Objetivo

Definir a estrutura canonica para projetos ativos em `PROJETOS/`, em que o
trabalho detalhado vive em manifestos proprios de issue e, quando necessario,
em arquivos proprios de task; a sprint permanece apenas como manifesto de
selecao, o intake antecede o PRD e a auditoria fecha a fase.

## Estrutura Canonica

```text
PROJETOS/<PROJETO>/
  INTAKE-<PROJETO>.md
  PRD-<PROJETO>.md
  AUDIT-LOG.md
  DECISION-PROTOCOL.md        (opcional, quando o projeto precisar de decisoes locais)
  feito/
  F1-<NOME-DA-FASE>/
    F1_<PROJETO>_EPICS.md
    EPIC-F1-01-<NOME>.md
    issues/
      ISSUE-F1-01-001-<NOME>/     (pasta) ou ISSUE-F1-01-001-<NOME>.md (legado)
        README.md                 manifesto da issue
        TASK-1.md
        TASK-2.md
    sprints/
      SPRINT-F1-01.md
    auditorias/
      RELATORIO-AUDITORIA-F1-R01.md
```

Intakes adicionais de remediacao podem coexistir na raiz no formato `INTAKE-<PROJETO>-<SLUG>.md`.

## Formato de Issue: Pasta vs Arquivo

- **Issue granularizada (pasta)**: `issues/ISSUE-F<N>-<NN>-<MMM>-<slug>/` contem `README.md`
  (manifesto) e `TASK-*.md` (uma task por arquivo). Este e o formato canonico
  para novas issues com tasks decupadas, multiplas tasks ou
  `task_instruction_mode: required`.
- **Issue legada (arquivo)**: `issues/ISSUE-F<N>-<NN>-<MMM>-<slug>.md` — formato anterior, ainda
  suportado por compatibilidade. Reservar para issue simples, local e de task
  unica, ou para preservar historico sem retrofit.
- Cada `TASK-N.md` deve seguir `PROJETOS/COMUM/TEMPLATE-TASK.md`.
- Links em epics e sprints: para issue granularizada, apontar para a pasta ou `README.md`.

## Responsabilidades por Documento

- `INTAKE-*.md`: usar `TEMPLATE-INTAKE.md`
- `PRD-*.md`: objetivo, arquitetura, requisitos, fases e restricoes do projeto
- `AUDIT-LOG.md`: usar `TEMPLATE-AUDITORIA-LOG.md`
- `F<N>_<PROJETO>_EPICS.md`: objetivo da fase, gate, tabela de epicos, dependencias e checklist de transicao do gate
- `EPIC-*.md`: manifesto do epico, DoD do epico, dependencias, artefato minimo e indice das issues
- `issues/ISSUE-*/` (pasta) ou `issues/ISSUE-*.md` (legado): user story, plano TDD, criterios
  `Given/When/Then`, DoD; quando granularizada, tasks em `TASK-*.md`; `decision_refs` e instructions
  por task quando exigidas; quando `task_instruction_mode: required` e a task envolver codigo,
  o plano TDD da issue deve descer para a task via `tdd_aplicavel` e `testes_red`; follow-up
  de review pos-issue deve preservar rastreabilidade explicita para a issue de origem
- `sprints/SPRINT-*.md`: selecao de issues, capacidade, riscos e consolidacao de status
- `auditorias/RELATORIO-AUDITORIA-*.md`: usar `TEMPLATE-AUDITORIA-RELATORIO.md`

## Template de `F<N>_<PROJETO>_EPICS.md`

```markdown
---
doc_id: "F1_PROJETO_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "YYYY-MM-DD"
audit_gate: "not_ready"
---

# Epicos - <PROJETO> / F1 - <Nome da Fase>

## Objetivo da Fase

## Gate de Saida da Fase

## Estado do Gate de Auditoria

- gate_atual: `not_ready`
- ultima_auditoria: `nao_aplicavel`

## Checklist de Transicao de Gate

> A semântica dos vereditos e as regras de julgamento vivem em `GOV-AUDITORIA.md`.

### `not_ready -> pending`
- [ ] todos os epicos estao `done`
- [ ] todas as issues filhas estao `done`
- [ ] DoD da fase foi revisado

### `pending -> hold`
- [ ] existe `RELATORIO-AUDITORIA-F<N>-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `hold`
- [ ] o estado do gate foi atualizado para `hold`

### `pending -> approved`
- [ ] existe `RELATORIO-AUDITORIA-F<N>-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `go`
- [ ] o estado do gate foi atualizado para `approved`

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F1-01 | Nome do epico | Resultado tecnico do epico | nenhuma | todo | [EPIC-F1-01-NOME.md](./EPIC-F1-01-NOME.md) |

## Dependencias entre Epicos

- `EPIC-F1-01`: nenhuma

## Escopo desta Fase

### Dentro
- ...

### Fora
- ...

## Definition of Done da Fase
- [ ]
```

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
| ISSUE-F1-01-001 | Nome da issue | Resultado tecnico unico | 3 | todo | [ISSUE-F1-01-001-NOME](./issues/ISSUE-F1-01-001-NOME/) |

## Artifact Minimo do Epico

## Dependencias
- [Intake](../INTAKE-PROJETO.md)
- [PRD](../PRD-PROJETO.md)
- [Fase](./F1_PROJETO_EPICS.md)
```

## Template de `issues/ISSUE-*/README.md` (Canonico)

```markdown
---
doc_id: "ISSUE-F1-01-001-NOME"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "YYYY-MM-DD"
task_instruction_mode: "optional"
decision_refs: []
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

## Tasks
- [T1 - Nome da task](./TASK-1.md)
- [T2 - Nome da task](./TASK-2.md)

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

Notas obrigatorias:

- o `README.md` concentra apenas o manifesto da issue
- o detalhamento operacional de cada task vive em `TASK-N.md`
- quando `task_instruction_mode: required`, os campos obrigatorios aparecem no
  corpo de cada `TASK-N.md`, nunca como bloco inline no `README.md`
- quando a task envolver codigo com cobertura automatizavel, `TASK-N.md` deve declarar
  `tdd_aplicavel: true` e descrever `testes_red` antes de `passos_atomicos`
- o status do `README.md` e agregado das tasks

Exemplo minimo de `TASK-1.md` quando TDD aplica:

```markdown
---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F1-01-001-NOME"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "YYYY-MM-DD"
tdd_aplicavel: true
---

## testes_red
- testes_a_escrever_primeiro:
  - ...
- comando_para_rodar:
  - `cd backend && python -m pytest -q -k contrato`
- criterio_red:
  - os testes devem falhar antes da implementacao
```

## Template de Compatibilidade Legada: `issues/ISSUE-*.md`

Usar apenas para issue simples, de task unica, ou para preservar artefato
historico sem migracao imediata.

```markdown
---
doc_id: "ISSUE-F1-01-001-NOME.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "YYYY-MM-DD"
task_instruction_mode: "optional"
decision_refs: []
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
- tdd_aplicavel: true
- testes_red:
  - testes_a_escrever_primeiro:
    - ...
  - comando_para_rodar:
    - `npm run test -- --run`
  - criterio_red:
    - os testes devem falhar antes da implementacao
- passos_atomicos:
  1. escrever os testes listados em `testes_red`
  2. rodar os testes e confirmar falha inicial
  3. implementar o minimo necessario para passar
  4. rodar os testes e confirmar green
  5. refatorar se necessario mantendo green
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

## Rastreabilidade de Follow-up de Review

- follow-up local gerado por revisao pos-issue nao reabre a issue original
- a nova issue deve permanecer no mesmo epico e fase enquanto a remediacao for
  local e contida
- a secao `Contexto Tecnico` da nova issue deve citar:
  - issue de origem
  - evidencia da revisao
  - sintoma observado
  - risco de nao corrigir
- a secao `Dependencias` deve incluir a issue de origem alem das referencias
  canonicas do projeto
- se o achado exceder ajuste local, a saida correta e `INTAKE-*.md`, nao nova
  issue local

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
| ISSUE-F1-01-001 | Nome da issue | 3 | todo | [ISSUE-F1-01-001-NOME](../issues/ISSUE-F1-01-001-NOME/) |

## Riscos e Bloqueios

## Encerramento
- decisao:
- observacoes:
```

## Regras de `task_instruction_mode`

- `optional`: tasks podem permanecer como checklist curto
- `required`: cada task precisa de bloco proprio em `## Instructions por Task` ou arquivo
  `TASK-N.md` quando a issue for granularizada
- em task com codigo e `tdd_aplicavel: true`, o detalhamento por task deve explicitar
  `testes_red` e ordem red -> green -> refactor
- usar `required` conforme `SPEC-TASK-INSTRUCTIONS.md`

## Status Agregado (Issue Granularizada)

Quando a issue for pasta com `TASK-*.md`, o status no `README.md` e derivado das tasks:

- `done`: todas as tasks `done`
- `active`: pelo menos uma task `active` ou `done`, mas nem todas `done`
- `todo`: todas as tasks `todo`
- `cancelled`: cancelamento explicito da issue

## Convencao de Links

- link Markdown relativo e a referencia canonica
- wikilink e complementar e nunca deve ser o unico meio de navegacao
- usar wikilinks qualificados por caminho local para evitar ambiguidade
