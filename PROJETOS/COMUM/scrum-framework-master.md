---
doc_id: "scrum-framework-master.md"
version: "1.4"
status: "active"
owner: "PM"
last_updated: "2026-03-08"
---

# scrum-framework-master

> Este documento define o fluxo canonico do repositorio `PROJETOS/`. O padrao aceito para projetos ativos e exclusivamente `issue-first`, com intake formal e gate formal de auditoria por fase.

## 1. Fluxo Canonico

```text
PROJETOS/COMUM/
  -> INTAKE-FRAMEWORK.md
  -> AUDITORIA-GOV.md
     -> INTAKE-<PROJETO>.md
     -> PRD-<PROJETO>.md
     -> AUDIT-LOG.md
     -> F<N>-<NOME>/
          -> F<N>_<PROJETO>_EPICS.md
          -> EPIC-F<N>-<NN>-<NOME>.md
          -> issues/ISSUE-F<N>-<NN>-<MMM>-<NOME>.md
          -> sprints/SPRINT-F<N>-<NN>.md
          -> auditorias/RELATORIO-AUDITORIA-F<N>-R<NN>.md
```

`Intake -> PRD -> Fases -> Epicos -> Issues -> Tasks -> Auditorias`

## 2. Premissas do Repositorio

- projetos ativos seguem apenas o padrao `issue-first`
- todo projeto ativo precisa ter `INTAKE-<PROJETO>.md`
- todo projeto ativo precisa ter `PRD-<PROJETO>.md`
- todo projeto ativo precisa ter `AUDIT-LOG.md`
- `done` e status documental; arquivamento fisico continua em `feito/`
- `BLOQUEADO` e `BLOCKED_LIMIT` sao estados operacionais, nao status canonicos persistidos

## 3. Artefatos Canonicos

| Artefato | Nome |
|---|---|
| Intake principal | `INTAKE-<PROJETO>.md` |
| Intake derivado | `INTAKE-<PROJETO>-<SLUG>.md` |
| PRD | `PRD-<PROJETO>.md` |
| Log de auditoria | `AUDIT-LOG.md` |
| Manifesto da fase | `F<N>_<PROJETO>_EPICS.md` |
| Manifesto do epico | `EPIC-F<N>-<NN>-<NOME>.md` |
| Issue | `ISSUE-F<N>-<NN>-<MMM>-<NOME>.md` |
| Sprint | `SPRINT-F<N>-<NN>.md` |
| Relatorio de auditoria | `RELATORIO-AUDITORIA-F<N>-R<NN>.md` |

## 4. Responsabilidade de Cada Artefato

- `INTAKE-*.md`: problema, oportunidade, publico, jobs, fluxo, restricoes, riscos, taxonomias, rastreabilidade e lacunas conhecidas para geracao do PRD
- `PRD-*.md`: objetivo, escopo, arquitetura, riscos, fases e criterios de fatiamento
- `AUDIT-LOG.md`: trilha cumulativa de auditorias, vereditos, achados materiais, follow-ups e supersedencia
- `F<N>_<PROJETO>_EPICS.md`: objetivo da fase, gate, escopo, epicos e estado do gate de auditoria
- `EPIC-*.md`: contexto arquitetural, objetivo tecnico, DoD do epico e indice das issues
- `ISSUE-*.md`: unidade executavel com TDD, criterios, DoD, tasks e instructions por task quando exigidas
- `SPRINT-*.md`: selecao operacional de issues e consolidacao de capacidade
- `auditorias/RELATORIO-AUDITORIA-*.md`: evidencia formal da rodada, veredito, classes de achado e handoff de remediacao

## 5. Status Canonicos

Status persistidos:

- `todo`
- `active`
- `done`
- `cancelled`

Regra derivada:

- `todo`: nenhum filho iniciado
- `active`: existe filho `active` ou `done`, mas nem todos estao `done`
- `done`: todos os filhos estao `done` e o DoD do pai foi fechado
- `cancelled`: cancelamento explicito com justificativa

## 6. Gate de Intake para PRD

A etapa `Intake -> PRD` so pode avancar quando o arquivo `INTAKE-*.md` contiver, no minimo:

- problema ou oportunidade clara
- publico e operador principal
- fluxo principal desejado
- escopo dentro e fora
- restricoes e riscos
- arquitetura afetada
- lacunas conhecidas
- `intake_kind` e `source_mode`
- rastreabilidade de origem quando houver backfill ou auditoria

Para `intake_kind: problem | refactor | audit-remediation`, tambem precisa conter:

- sintoma observado
- impacto operacional
- evidencia tecnica
- componente(s) afetado(s)
- riscos de nao agir

## 7. Gate de Auditoria da Fase

A fase so pode ser movida para `feito/` quando:

1. todos os epicos estiverem `done`
2. o gate de auditoria estiver `approved`
3. houver relatorio `RELATORIO-AUDITORIA-F<N>-R<NN>.md`
4. o `AUDIT-LOG.md` registrar a rodada com commit SHA valido

A auditoria deve avaliar:

- aderencia ao intake, PRD, fase, epicos e issues
- bugs e regressoes provaveis
- code smells
- arquivos e funcoes monoliticas
- ausencia de docstrings em codigo compartilhado, publico ou complexo
- cobertura de testes e rastreabilidade das evidencias

## 8. Regras de Remediacao por Auditoria

- correcao local e contida pode abrir `issue-local` na mesma fase
- remediacao estrutural ou sistemica deve abrir novo `INTAKE-*` com `intake_kind: audit-remediation`
- follow-up estrutural exige handoff no relatorio com nome sugerido, problema resumido, evidencias, impacto e escopo presumido
- `AUDIT-LOG.md` deve registrar se o destino do `hold` foi `issue-local`, `new-intake` ou `cancelled`

## 9. Contratos Operacionais

- intake: preenche `INTAKE-*.md`
- geracao de PRD: transforma `INTAKE-*.md` em `PRD-*.md` sem inventar lacunas criticas
- planejamento: desdobra o PRD em fases, epicos, issues e sprints quando necessario
- execucao: implementa exatamente a issue elegivel
- auditoria: valida aderencia e saude estrutural antes do fechamento da fase
