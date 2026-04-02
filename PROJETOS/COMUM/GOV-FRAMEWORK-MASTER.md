---
doc_id: "GOV-FRAMEWORK-MASTER.md"
version: "3.0"
status: "active"
owner: "PM"
last_updated: "2026-03-30"
---

# GOV-FRAMEWORK-MASTER

> Este documento e o mapa de alto nivel do framework. As regras detalhadas de intake,
> scrum, auditoria, limites e execucao vivem em documentos especializados e devem ser
> referenciadas, nao copiadas.

## 0. Abordagem Delivery-First

> O framework utiliza o principio **delivery-first** para planejamento de projetos de codigo.
> No planejamento documental, esse principio se materializa como **feature-first** na **arvore
> de entrega** sob `features/` (manifestos, user stories e tasks), nao como obrigatorio de
> embutir Features ou User Stories no corpo do PRD. O PRD e contrato estrategico; o desdobramento
> entregavel e etapa explicita do pipeline (`GOV-PRD.md`, `SESSION-CLARIFICAR-INTAKE.md`, prompts `PROMPT-*-PARA-*`, sessoes
> `SESSION-DECOMPOR-*` quando aplicavel).
>
> Ver: `GOV-PRD.md` e `TEMPLATE-PRD.md` para o contrato do PRD; `TEMPLATE-FEATURE.md` para manifesto
> de feature; `GOV-BRANCH-STRATEGY.md` para estrategia de branches.

## 1. Estrutura Canonica do Repositorio

```text
PROJETOS/
  COMUM/
    boot-prompt.md
    GOV-*.md
    SPEC-*.md
    TEMPLATE-*.md
    PROMPT-*.md
    SESSION-*.md
  <PROJETO>/
    INTAKE-<PROJETO>.md
    PRD-<PROJETO>.md
    AUDIT-LOG.md
    features/
      FEATURE-<N>-<NOME>/
        FEATURE-<N>.md
        user-stories/
          US-<N>-<NN>-<NOME>/
            README.md
            REV-US-<N>-<NN>.md
            TASK-1.md
        auditorias/
          RELATORIO-AUDITORIA-F<N>-R<NN>.md
    encerramento/
      RELATORIO-ENCERRAMENTO.md
```

A cadeia operacional do framework vive em `GOV-SCRUM.md`.

## 2. Premissas do Repositorio

- a cadeia normativa e `Intake -> Clarificacao -> PRD -> Features -> User Stories -> Tasks -> Execucao -> Review -> Auditoria de Feature`; o PRD nao substitui manifestos nem lista Features/US (`GOV-PRD.md`)
- o planeamento e a entrega seguem a hierarquia **Feature > User Story > Task** na arvore sob `features/`; o mapa de pastas alvo para esse modelo esta na secao `1. Estrutura Canonica do Repositorio`
- todo projeto ativo precisa ter `INTAKE-<PROJETO>.md`, `PRD-<PROJETO>.md` e `AUDIT-LOG.md`
- artefatos em `PROJETOS/COMUM/` usam prefixos funcionais: `GOV-`, `TEMPLATE-`, `PROMPT-`, `SESSION-`, `SPEC-`
- o contrato de ciclo de trabalho, estados operacionais e Definition of Done do framework vive em `GOV-SCRUM.md` (nao duplicar aqui)
- `GOV-ISSUE-FIRST.md`, `GOV-SPRINT-LIMITES.md` e `SPEC-T1-ESTADO-ATUAL-FRAMEWORK-OPENCLAW.md` permanecem apenas como stubs de compatibilidade; o conteudo historico saiu do clone lean e nao define a superficie operacional ativa do v3.0

## 3. Fontes de Verdade por Tema

| Tema | Fonte primaria |
|---|---|
| contrato do PRD (sem Features/US no documento) | `GOV-PRD.md` |
| clarificacao pre-PRD | `SESSION-CLARIFICAR-INTAKE.md` |
| manifesto de feature e decomposicao Feature -> US | `GOV-FEATURE.md` |
| ciclo de trabalho, status e DoD | `GOV-SCRUM.md` |
| auditoria (contrato geral do gate de feature) | `GOV-AUDITORIA.md` |
| gate `Intake -> PRD` e taxonomias | `GOV-INTAKE.md` |
| contratos de execucao com side effect | `GOV-WORK-ORDER.md` |
| tamanho e DoD de User Story | `GOV-USER-STORY.md` |
| auditoria de feature | `GOV-AUDITORIA-FEATURE.md` |
| auditoria ad hoc do framework/repositorio | `PROMPT-AUDITORIA-FRAMEWORK.md` |
| encerramento de projeto | `TEMPLATE-ENCERRAMENTO.md` |
| rules de `task_instruction_mode` | `SPEC-TASK-INSTRUCTIONS.md` |
| commit apos cada task | `GOV-COMMIT-POR-TASK.md` |
| gate automatico de task/commit/handoff antes de `ready_for_review` | `scripts/framework_governance/validate_us_traceability.py` |
| varrimento CI de US em `ready_for_review` (task/commit/handoff) | `scripts/framework_governance/scan_us_traceability.py` |
| thresholds anti-monolito | `SPEC-ANTI-MONOLITO.md` |
| leitura minima guiada por evidencia | `SPEC-LEITURA-MINIMA-EVIDENCIA.md` |
| traces de sessao auditaveis | `SPEC-SESSION-TRACE-AUDITAVEL.md` |
| decisoes estruturais compartilhadas | `GOV-DECISOES.md` |
| operacao interativa em chat | `SESSION-MAPA.md` |
| read model operacional obrigatorio (Postgres, pgvector, sync desde Git) | `SPEC-INDICE-PROJETOS-POSTGRES.md` |
| quando sync Postgres e obrigatorio vs opcional; URL ausente; anti-exploracao de instalacao | `SPEC-RUNTIME-POSTGRES-MATRIX.md` |
| cabecalho `imp-N.md` por task | `TEMPLATE-IMP-SESSAO.md` |
| ferramenta canonica para leitura por preview/faixa/ancora | `scripts/session_tools/read_file.py` |
| edicao de artefatos Markdown (encoding, patches) | `SPEC-EDITOR-ARTEFACTOS.md` |
| pytest, venv e shell no Windows | `RUNTIME-WINDOWS.md` |
| migracao normativa PRD sem Features/US no documento (pipeline em etapas) | `SPEC-PIPELINE-PRD-SEM-FEATURES.md` |
| estrategia de branches | `GOV-BRANCH-STRATEGY.md` |

## 4. Artefatos Canonicos do Projeto

| Artefato | Nome |
|---|---|
| intake principal | `INTAKE-<PROJETO>.md` |
| intake derivado | `INTAKE-<PROJETO>-<SLUG>.md` |
| PRD | `PRD-<PROJETO>.md` |
| log de auditoria | `AUDIT-LOG.md` |
| manifesto da feature | `features/FEATURE-<N>-<NOME>/FEATURE-<N>.md` |
| user story canonica | `features/FEATURE-<N>-<NOME>/user-stories/US-<N>-<NN>-<NOME>/README.md` |
| entrada local revisao pos-US (opcional) | `features/FEATURE-<N>-<NOME>/user-stories/US-<N>-<NN>-<NOME>/REV-US-<N>-<NN>.md` |
| task canonica | `features/FEATURE-<N>-<NOME>/user-stories/US-<N>-<NN>-<NOME>/TASK-<N>.md` |
| cabecalho opcional de sessao por task | `imp-<N>.md` na pasta da US — ver `TEMPLATE-IMP-SESSAO.md` |
| relatorio de auditoria | `features/FEATURE-<N>-<NOME>/auditorias/RELATORIO-AUDITORIA-F<N>-R<NN>.md` |
| relatorio de encerramento | `encerramento/RELATORIO-ENCERRAMENTO.md` |

## 5. Modos de Operacao

- `boot-prompt.md`: entrada para Cloud Agent autonomo; descobre a proxima `Feature` ativa, a proxima `User Story` elegivel e a proxima `Task` elegivel, ou entra em auditoria de feature quando aplicavel; a descoberta baseia-se em **Markdown + Git** sob `PROJETOS/<PROJETO>/`; o read model Postgres e operacional, mas nunca substitui os ficheiros
- `SESSION-MAPA.md`: entrada para chat interativo; o humano escolhe o prompt
  e informa os parametros da sessao; intake, clarificacao e PRD continuam humanos; apos PRD
  aprovado, o desdobramento em Features, User Stories e Tasks e **explicito**
  (prompts e sessoes dedicadas); a execucao segue a hierarquia `Feature > User Story > Task`
  com gates do agente senior, e qualquer override humano vira excecao explicita

## 6. Responsabilidade Deste Documento

- descrever o mapa completo do framework
- registrar quais documentos sao normativos para cada tema
- evitar duplicacao de gate, veredito, checklist ou threshold ja definido em outro artefato
- nao redefinir cadeia de trabalho, status ou Definition of Done aqui; use `GOV-SCRUM.md`

Regras detalhadas de intake nao devem ser redefinidas aqui. Use `GOV-INTAKE.md`.
Regras detalhadas de auditoria nao devem ser redefinidas aqui. Use `GOV-AUDITORIA.md`.
Regras detalhadas de task instructions nao devem ser redefinidas aqui. Use `SPEC-TASK-INSTRUCTIONS.md`.
