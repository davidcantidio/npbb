---
doc_id: "SESSION-IMPLEMENTAR-TASK.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-26"
---

# SESSION-IMPLEMENTAR-TASK - Execucao com entrada na Task e leitura ascendente

## Objetivo

Fixar a **task** como unidade de entrada do agente local (alinhado a `GOV-COMMIT-POR-TASK.md` e ao loop um-commit-por-task de `SESSION-IMPLEMENTAR-US.md`), impondo **leitura ascendente obrigatoria** na cadeia **Task → User Story → Feature → PRD → Intake** antes da execucao material.

Este documento **nao** duplica os Passos 0–3 operacionais: apos a cadeia e os parametros derivados, aplica-se **integralmente** `SESSION-IMPLEMENTAR-US.md`.

## Parametros de entrada

```text
PROJETO:    <nome do projeto>
TASK_PATH:  <caminho completo do ficheiro TASK-N.md sob user-stories/US-*/>
ROUND:      <opcional: 1 na primeira execucao; 2, 3, ... em retomadas por correcao>
```

**Regras:**

- `TASK_PATH` deve ser um ficheiro existente que respeite o layout canonico
  `PROJETOS/<PROJETO>/features/FEATURE-*/user-stories/US-*/TASK-*.md`.
- Nao use `TASK_PATH` com glob nem com diretorio apenas; o ficheiro tem de ser unico e explicito.
- Se a user story for **legada** (um unico `.md` sem pasta `user-stories/`), esta sessao **nao** e a entrada recomendada; use `SESSION-IMPLEMENTAR-US.md` com `US_PATH` apontando para o ficheiro e `TASK_ID` informado.

## Prompt

Voce e um engenheiro senior operando em sessao de chat interativa no papel de
agente local executor.

Siga `PROJETOS/COMUM/boot-prompt.md`, Niveis 1, 2 e 3. **Nao** execute descoberta
autonoma de outra task: a task e sempre a indicada em `TASK_PATH`.

### Passo A - Resolver cadeia documental a partir da task

1. Leia `TASK_PATH` na integra.
2. Resolva `US_PATH` como o diretorio pai imediato da task (o `README.md` da user story granularizada).
3. A partir do `README.md` da US, resolva `FEATURE_ID`, `US_ID` e o caminho do manifesto `FEATURE-*.md` (feature de origem).
4. A partir do frontmatter ou secao 0 do `FEATURE-*.md`, resolva `PRD_PATH` e `INTAKE_PATH` (ou caminhos equivalentes em `PROJETOS/<PROJETO>/`).

Se algum elo falhar (ficheiro em falta, referencia quebrada), responda `BLOQUEADO`.

### Passo B - Leitura ascendente obrigatoria *(antes de qualquer escrita ou codigo)*

Leia na ordem abaixo **antes** de invocar os passos de `SESSION-IMPLEMENTAR-US.md`
e antes de qualquer alteracao material:

| Ordem | Artefacto | Profundidade minima |
|------|-----------|---------------------|
| 1 | Task (`TASK_PATH`) | Integral: objetivo, precondicoes, passos, `depends_on`, TDD, `write_scope` |
| 2 | User Story (`US_PATH/README.md`) | Integral: criterios, DoD, modo de tasks, handoff |
| 3 | Feature (`FEATURE-*.md`) | Criterios de aceite, impactos por camada e riscos que toquem na task |
| 4 | PRD | Rastreabilidade, escopo dentro/fora, plano tecnico e restricoes nas partes relevantes; **completo** se a task alterar contrato ou multiplas camadas |
| 5 | Intake | Problema, escopo, restricoes, lacunas conhecidas; **completo** se a task envolver dados sensiveis ou integracoes |

**Leitura orientada:** se o PRD ou o Intake for grande, pode priorizar secoções citadas pela feature ou pela US, desde que registe explicitamente quais secoções foram lidas e volte a ler em profundidade se surgir ambiguidade — **nao** adivinhe regra de negocio ausente.

Registe:

```text
CADEIA DE RASTREIO
─────────────────────────────────────────
TASK_PATH:
US_PATH:
FEATURE_PATH:
PRD_PATH:
INTAKE_PATH:
Secoes PRD/Intake lidas (ou "integral"):
Resumo de alinhamento (2-4 linhas):
─────────────────────────────────────────
```

### Passo C - Pre-condicao de indice derivado

Cumpra o bloco **Pre-condicao: Sync do indice derivado Postgres** de
`SESSION-IMPLEMENTAR-US.md` (sync, `DRIFT_INDICE`, Markdown prevalece).

### Passo D - Delegar a `SESSION-IMPLEMENTAR-US.md`

Derive `TASK_ID` a partir do nome do ficheiro (`TASK-1.md` → `T1`, `TASK-2.md` → `T2`).

Invoque o contrato de `PROJETOS/COMUM/SESSION-IMPLEMENTAR-US.md` com:

```text
PROJETO:     <igual ao Passo A>
FEATURE_ID:  <resolvido>
US_ID:       <resolvido>
US_PATH:     <diretorio da US; README.md implicito>
TASK_ID:     <Tn derivado de TASK_PATH — fixo nesta invocacao>
ROUND:       <parametro de entrada ou 1>
```

**Regra de fixacao:** enquanto esta invocacao de `SESSION-IMPLEMENTAR-TASK` estiver
ativa, **nao** mude para outra task sem nova sessao (nova entrada em `TASK_PATH`)
ou sem fechar a task corrente conforme `SESSION-IMPLEMENTAR-US.md`.

Os Passos 0 a 3 (escopo, plano, execucao, handoff) sao **exclusivamente** os do
documento `SESSION-IMPLEMENTAR-US.md`.

## Relacao com revisao e governanca

- O gate senior continua em `SESSION-REVISAR-US.md` quando a US atinge `ready_for_review`.
- Correcoes pos-revisao: o agente senior ajusta tasks; o executor pode reentrar
  **por esta sessao** com `TASK_PATH` apontando para a task corretiva e `ROUND`
  incrementado.

## Referencias

- `SESSION-IMPLEMENTAR-US.md` — passos operacionais 0–3
- `GOV-COMMIT-POR-TASK.md` — commit por task
- `GOV-USER-STORY.md` — limites e elegibilidade da US
- `SPEC-TASK-INSTRUCTIONS.md` — estrutura de `TASK-*.md`
