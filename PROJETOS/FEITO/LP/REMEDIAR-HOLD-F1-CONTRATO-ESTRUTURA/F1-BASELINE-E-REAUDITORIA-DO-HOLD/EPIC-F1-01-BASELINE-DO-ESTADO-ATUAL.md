---
doc_id: "EPIC-F1-01-BASELINE-DO-ESTADO-ATUAL.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-13"
---

# EPIC-F1-01 - Baseline do Estado Atual

## Objetivo

Produzir uma baseline objetiva do estado atual do repositorio para provar, item
a item, o que do PRD derivado e da auditoria F1 ja esta implementado, o que
virou no-op controlado e o que permanece como risco residual para reauditoria.

## Resultado de Negocio Mensuravel

O PM e a futura auditoria deixam de depender do texto historico do hold como
fonte unica e passam a ter uma matriz rastreavel entre achados originais e
estado real do codigo, suficiente para delimitar o que ainda precisa de prova e
o que nao deve voltar ao backlog funcional.

## Contexto Arquitetural

Este epic consome o intake e o PRD derivados do hold, o `AUDIT-LOG.md`, a
auditoria `auditoria_fluxo_ativacao.md`, a F1 original e as superficies reais
do fluxo publico (`landing_pages.py`, `landing_page_submission.py`,
`leads.py`, `landing_public.py`, `EventLandingPage.tsx` e testes correlatos).
Nao executa refactor estrutural; ele apenas mede, compara e classifica.

## Definition of Done do Epico

- [x] a matriz de achados originais vs estado atual existe e esta objetiva
- [x] os achados do hold foram classificados como `implementado`, `nao_aplicavel` ou `residual`
- [x] a baseline estrutural de `models.py` e `ativacao.py` esta documentada
- [x] `backend/app/routers/leads.py` aparece como risco residual explicito e fora deste sibling

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-01-001 | Classificar PRD vs repo no fluxo publico | Produzir a matriz rastreavel entre PRD, auditoria e estado atual do fluxo publico. | 3 | done | [ISSUE-F1-01-001-CLASSIFICAR-PRD-VS-REPO-NO-FLUXO-PUBLICO.md](./issues/ISSUE-F1-01-001-CLASSIFICAR-PRD-VS-REPO-NO-FLUXO-PUBLICO.md) |
| ISSUE-F1-01-002 | Validar baseline estrutural da F1 | Medir os alvos estruturais do hold e registrar o risco residual fora do sibling. | 2 | done | [ISSUE-F1-01-002-VALIDAR-BASELINE-ESTRUTURAL-DA-F1.md](./issues/ISSUE-F1-01-002-VALIDAR-BASELINE-ESTRUTURAL-DA-F1.md) |

## Artifact Minimo do Epico

Baseline rastreavel registrada nas issues `ISSUE-F1-01-001` e
`ISSUE-F1-01-002`, com classificacao dos achados do hold e quadro estrutural
dos arquivos alvo da F1.

## Dependencias

- [Intake Derivado](../../INTAKE-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md)
- [PRD Derivado](../../PRD-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md)
- [Audit Log](../../AUDIT-LOG.md)
- [Auditoria de Origem](../../auditoria_fluxo_ativacao.md)
- [F1 Original](../../F1-FUNDACAO-MODELO-BACKEND/F1_LP_EPICS.md)
- [Fase](./F1_REMEDIAR_HOLD_F1_CONTRATO_ESTRUTURA_EPICS.md)
