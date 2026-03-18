---
doc_id: "GOV-FRAMEWORK-MASTER.md"
version: "2.3"
status: "active"
owner: "PM"
last_updated: "2026-03-18"
---

# GOV-FRAMEWORK-MASTER

> Este documento e o mapa de alto nivel do framework. As regras detalhadas de intake,
> scrum, auditoria, limites e execucao vivem em documentos especializados e devem ser
> referenciadas, nao copiadas.

## 0. Abordagem Delivery-First

> O framework utiliza o principio **delivery-first** para planejamento de projetos de codigo.
> No planejamento documental, esse principio se materializa como **feature-first**.
> O eixo principal sao as **features** (comportamentos entregaveis), nao as camadas tecnicas
> (banco/backend/frontend). A arquitetura aparece como impacto de cada feature, nao como
> organizacao principal.
>
> Ver: `TEMPLATE-PRD.md` para estrutura de features, `GOV-BRANCH-STRATEGY.md` para estrategia de branches.

## 1. Estrutura Canonica do Repositorio

```text
PROJETOS/
  boot-prompt.md
  COMUM/
    GOV-FRAMEWORK-MASTER.md
    GOV-SCRUM.md
    GOV-INTAKE.md
    GOV-AUDITORIA.md
    GOV-SPRINT-LIMITES.md
    GOV-WORK-ORDER.md
    GOV-COMMIT-POR-TASK.md
    GOV-DECISOES.md
    GOV-ISSUE-FIRST.md
    GOV-BRANCH-STRATEGY.md          (delivery-first / feature-first)
    SPEC-TASK-INSTRUCTIONS.md
    SPEC-ANTI-MONOLITO.md
    TEMPLATE-PRD.md                  (delivery-first / feature-first)
    TEMPLATE-INTAKE.md
    PROMPT-*.md
    SESSION-*.md
  <PROJETO>/
    INTAKE-<PROJETO>.md
    PRD-<PROJETO>.md
    AUDIT-LOG.md
    feito/
    F<N>-<NOME>/
      F<N>_<PROJETO>_EPICS.md
      EPIC-F<N>-<NN>-<NOME>.md
      issues/
        ISSUE-F<N>-<NN>-<MMM>-<NOME>/
          README.md
          TASK-1.md
        ISSUE-F<N>-<NN>-<MMM>-<NOME>.md   (legado)
      sprints/SPRINT-F<N>-<NN>.md
      auditorias/RELATORIO-AUDITORIA-F<N>-R<NN>.md
```

A cadeia operacional do framework vive em `GOV-SCRUM.md`.

## 2. Premissas do Repositorio

- projetos ativos seguem apenas o padrao `issue-first`
- todo projeto ativo precisa ter `INTAKE-<PROJETO>.md`, `PRD-<PROJETO>.md` e `AUDIT-LOG.md`
- artefatos em `PROJETOS/COMUM/` usam prefixos funcionais: `GOV-`, `TEMPLATE-`, `PROMPT-`, `SESSION-`, `SPEC-`
- regras de status, estados operacionais e arquivamento de fase vivem em `GOV-SCRUM.md`

## 3. Fontes de Verdade por Tema

| Tema | Fonte primaria |
|---|---|
| ciclo de trabalho, status e DoD | `GOV-SCRUM.md` |
| gate `Intake -> PRD` e taxonomias | `GOV-INTAKE.md` |
| auditoria de fase, vereditos e remediacao | `GOV-AUDITORIA.md` |
| limites de sprint e tamanho | `GOV-SPRINT-LIMITES.md` |
| contratos de execucao com side effect | `GOV-WORK-ORDER.md` |
| estrutura de fase, epico, issue e sprint | `GOV-ISSUE-FIRST.md` |
| rules de `task_instruction_mode` | `SPEC-TASK-INSTRUCTIONS.md` |
| commit apos cada task | `GOV-COMMIT-POR-TASK.md` |
| thresholds anti-monolito | `SPEC-ANTI-MONOLITO.md` |
| decisoes estruturais compartilhadas | `GOV-DECISOES.md` |
| operacao interativa em chat | `SESSION-MAPA.md` |
| estrategia de branches | `GOV-BRANCH-STRATEGY.md` |

## 4. Artefatos Canonicos do Projeto

| Artefato | Nome |
|---|---|
| intake principal | `INTAKE-<PROJETO>.md` |
| intake derivado | `INTAKE-<PROJETO>-<SLUG>.md` |
| PRD | `PRD-<PROJETO>.md` |
| log de auditoria | `AUDIT-LOG.md` |
| manifesto da fase | `F<N>_<PROJETO>_EPICS.md` |
| manifesto do epico | `EPIC-F<N>-<NN>-<NOME>.md` |
| issue canonica | `ISSUE-F<N>-<NN>-<MMM>-<NOME>/README.md` |
| task canonica | `ISSUE-F<N>-<NN>-<MMM>-<NOME>/TASK-<N>.md` |
| issue legada | `ISSUE-F<N>-<NN>-<MMM>-<NOME>.md` |
| sprint | `SPRINT-F<N>-<NN>.md` |
| relatorio de auditoria | `RELATORIO-AUDITORIA-F<N>-R<NN>.md` |

## 5. Modos de Operacao

- `boot-prompt.md`: entrada para Cloud Agent autonomo; descobre a unidade elegivel e executa
- `SESSION-MAPA.md`: entrada para chat interativo; o PM escolhe o prompt de sessao e acompanha as confirmacoes HITL

## 6. Responsabilidade Deste Documento

- descrever o mapa completo do framework
- registrar quais documentos sao normativos para cada tema
- evitar duplicacao de gate, veredito, checklist ou threshold ja definido em outro artefato
- nao redefinir cadeia de trabalho, status ou Definition of Done aqui; use `GOV-SCRUM.md`

Regras detalhadas de intake nao devem ser redefinidas aqui. Use `GOV-INTAKE.md`.
Regras detalhadas de auditoria nao devem ser redefinidas aqui. Use `GOV-AUDITORIA.md`.
Regras detalhadas de task instructions nao devem ser redefinidas aqui. Use `SPEC-TASK-INSTRUCTIONS.md`.
