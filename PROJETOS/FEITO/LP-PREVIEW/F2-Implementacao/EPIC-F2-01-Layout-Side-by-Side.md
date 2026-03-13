---
doc_id: "EPIC-F2-01-Layout-Side-by-Side.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
---

# EPIC-F2-01 - Layout Side-by-Side

## Objetivo

Converter o layout da pagina de configuracao para duas colunas (painel esquerdo + preview direito), reposicionando o preview a direita fixo e visivel durante toda a sessao, sem necessidade de scroll.

## Resultado de Negocio Mensuravel

Operador pode correlacionar configuracao com preview visual em tempo real, sem rolar a tela para ver o resultado.

## Contexto Arquitetural

- F1 Discovery fornece mapeamento de componentes e estrutura atual
- EventLeadFormConfigPage usa Paper com Stack de secoes; PreviewSection intercalada
- Reatividade via useLandingPreview e previewEventoLanding

## Definition of Done do Epico
- [ ] Layout de duas colunas implementado
- [ ] Preview reposicionado a direita, fixo
- [ ] Preview visivel durante toda a sessao
- [ ] Reatividade preservada

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F2-01-001 | Converter layout para duas colunas painel + preview | Grid/flex duas colunas, painel esquerdo scrollavel, preview direito fixo | 5 | todo | [ISSUE-F2-01-001-Converter-Layout-Duas-Colunas.md](./issues/ISSUE-F2-01-001-Converter-Layout-Duas-Colunas.md) |

## Artifact Minimo do Epico

- EventLeadFormConfigPage com layout side-by-side funcional
- PreviewSection integrada ao lado direito

## Dependencias
- [Intake](../../INTAKE-LP-PREVIEW.md)
- [PRD](../../PRD-LP-PREVIEW.md)
- [Fase](./F2_LP-PREVIEW_EPICS.md)
- [F1 Discovery](../../F1-Discovery-Tecnico/F1_LP-PREVIEW_EPICS.md) — concluida
