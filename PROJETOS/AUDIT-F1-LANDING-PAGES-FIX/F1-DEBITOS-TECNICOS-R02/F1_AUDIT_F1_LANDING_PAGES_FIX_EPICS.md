---
doc_id: "F1_AUDIT_F1_LANDING_PAGES_FIX_EPICS.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-08"
---

# Epicos - AUDIT-F1-LANDING-PAGES-FIX / F1 - DEBITOS-TECNICOS-R02

## Objetivo da Fase

Resolver os 3 achados nao bloqueantes da auditoria F1-R02 (S-01, S-02, S-03): decompor landingStyle.tsx em modulos coesos, remover campos mortos de LayoutVisualSpec e corrigir status documental do EPIC-F1-03.

## Gate de Saida da Fase

landingStyle.tsx com no maximo 25 linhas (re-exports); LayoutVisualSpec sem campos mortos; EPIC-F1-03 marcado como done; tsc e suite de testes da landing passando.

## Gate de Auditoria da Fase

- estado_do_gate: `not_ready`
- ultima_auditoria: nenhuma
- veredito_atual: n-a
- relatorio_mais_recente: n-a
- log_do_projeto: [AUDIT-LOG](../AUDIT-LOG.md)
- convencao_de_relatorios: [README](./auditorias/README.md)

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F1-01 | Housekeeping Documental | Corrigir inconsistencia de status EPIC-F1-03 (S-03) | nenhuma | done | [EPIC-F1-01-HOUSEKEEPING-DOCUMENTAL.md](./EPIC-F1-01-HOUSEKEEPING-DOCUMENTAL.md) |
| EPIC-F1-02 | Refatoracao Estrutural landingStyle | Decompor landingStyle.tsx e limpar LayoutVisualSpec (S-01, S-02) | nenhuma | todo | [EPIC-F1-02-REFATORACAO-LANDING-STYLE.md](./EPIC-F1-02-REFATORACAO-LANDING-STYLE.md) |

## Dependencias entre Epicos

- `EPIC-F1-01`: nenhuma — pode iniciar imediatamente
- `EPIC-F1-02`: nenhuma — ISSUE-F1-02-002 depende de ISSUE-F1-02-001 (ordem interna)

```
EPIC-F1-01 ──► (independente)
EPIC-F1-02 ──► ISSUE-F1-02-001 → ISSUE-F1-02-002
```

## Escopo desta Fase

### Dentro

- correcao de status EPIC-F1-03 para done no manifesto LANDING-PAGE-FORM-FIRST
- decomposicao de landingStyle.tsx em landingTheme.ts, landingOverlays.tsx, landingLayout.ts, landingCardStyles.ts
- re-export shim em landingStyle.tsx (max 25 linhas)
- remocao de campos mortos de LayoutVisualSpec
- renomear heroTextColor para pageTextColor

### Fora

- alteracao de comportamento visual
- alteracao de contrato de API
- novos testes
- refatoracao de landingSections ou outros modulos

## Definition of Done da Fase

- [ ] EPIC-F1-03 marcado como done no manifesto F1 do LANDING-PAGE-FORM-FIRST
- [ ] landingStyle.tsx com no maximo 25 linhas
- [ ] LayoutVisualSpec sem campos mortos
- [ ] tsc --noEmit passa
- [ ] suite de testes da landing passa
- [ ] gate de auditoria preparado para futura rodada em `auditorias/`

## Navegacao Rapida

- [Intake](../INTAKE-AUDIT-F1-LANDING-PAGES-FIX.md)
- [PRD](../PRD-DEBITOS-TECNICOS-R02-v1.0.md)
- [Audit Log](../AUDIT-LOG.md)
- [Epic F1-01](./EPIC-F1-01-HOUSEKEEPING-DOCUMENTAL.md)
- [Epic F1-02](./EPIC-F1-02-REFATORACAO-LANDING-STYLE.md)
