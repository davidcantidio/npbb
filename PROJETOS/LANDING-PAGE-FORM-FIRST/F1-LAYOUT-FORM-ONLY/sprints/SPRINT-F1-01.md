---
doc_id: "SPRINT-F1-01.md"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# SPRINT-F1-01

## Objetivo da Sprint

Construir os componentes base do novo layout: FullPageBackground com fundo tematico, FormCard centralizado e MinimalFooter. Ao final da sprint, os 3 componentes existem isoladamente e podem ser integrados.

## Capacidade

- story_points_planejados: 13
- issues_planejadas: 4
- override: nenhum

## Issues Selecionadas

| Issue ID | Nome | SP | Status | Documento |
|---|---|---|---|---|
| ISSUE-F1-01-001 | Criar FullPageBackground | 3 | done | [ISSUE-F1-01-001-CRIAR-FULLPAGEBACKGROUND.md](../issues/ISSUE-F1-01-001-CRIAR-FULLPAGEBACKGROUND.md) |
| ISSUE-F1-01-002 | Adaptar renderGraphicOverlay | 3 | done | [ISSUE-F1-01-002-ADAPTAR-RENDER-GRAPHIC-OVERLAY.md](../issues/ISSUE-F1-01-002-ADAPTAR-RENDER-GRAPHIC-OVERLAY.md) |
| ISSUE-F1-02-001 | Criar FormCard | 5 | done | [ISSUE-F1-02-001-CRIAR-FORMCARD.md](../issues/ISSUE-F1-02-001-CRIAR-FORMCARD.md) |
| ISSUE-F1-02-002 | Criar MinimalFooter | 2 | done | [ISSUE-F1-02-002-CRIAR-MINIMAL-FOOTER.md](../issues/ISSUE-F1-02-002-CRIAR-MINIMAL-FOOTER.md) |

## Riscos e Bloqueios

- renderGraphicOverlay pode assumir posicionamento DOM especifico do layout antigo — validar container antes
- tokens de getLayoutVisualSpec podem retornar valores dependentes do hero — mapear quais sao relevantes

## Encerramento

- decisao: concluida
- observacoes: ISSUE-F1-01-001, ISSUE-F1-01-002, ISSUE-F1-02-001 e ISSUE-F1-02-002 concluidas; componentes base prontos para integracao total.

## Saldo de Refacao Identificado Depois da Integracao

- rebatizar os tokens visuais herdados de hero em `landingStyle.tsx`
- remover campos de layout sem consumidor no modelo form-only
- manter `FullPageBackground` e overlay como entregas consolidadas, atuando apenas na semantica interna e nao no comportamento visual

## Navegacao Rapida

- [Epic F1-01](../EPIC-F1-01-FUNDO-TEMATICO-E-CONTAINER.md)
- [Epic F1-02](../EPIC-F1-02-CARD-FORMULARIO-E-RODAPE.md)
- `[[../issues/ISSUE-F1-01-001-CRIAR-FULLPAGEBACKGROUND]]`
- `[[../issues/ISSUE-F1-01-002-ADAPTAR-RENDER-GRAPHIC-OVERLAY]]`
- `[[../issues/ISSUE-F1-02-001-CRIAR-FORMCARD]]`
- `[[../issues/ISSUE-F1-02-002-CRIAR-MINIMAL-FOOTER]]`
