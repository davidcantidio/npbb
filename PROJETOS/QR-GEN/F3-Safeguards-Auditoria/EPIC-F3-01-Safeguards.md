---
doc_id: "EPIC-F3-01-Safeguards.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
---

# EPIC-F3-01 - Safeguards

## Objetivo

Implementar guard em `hydrate_ativacao_public_urls` ou no fluxo de persistencia que levante erro ou warning quando, em ambiente de producao (detectado por env ou flag), a URL calculada contiver host local. Incluir teste automatizado cobrindo producao vs dev.

## Resultado de Negocio Mensuravel

Regressao futura (URL local persistida em producao) detectavel em CI ou em runtime.

## Contexto Arquitetural

- `backend/app/services/landing_pages.py` — `hydrate_ativacao_public_urls`
- `backend/app/utils/urls.py` — `get_public_app_base_url`, `build_ativacao_public_urls`
- Deteccao de ambiente: `PUBLIC_APP_BASE_URL` ou variavel como `ENVIRONMENT=production`

## Definition of Done do Epico
- [ ] Guard implementado
- [ ] Teste automatizado passando
- [ ] Comportamento em dev local preservado

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F3-01-001 | Guard Producao URL Local | Guard e teste producao vs dev | 3 | todo | [ISSUE-F3-01-001-Guard-Producao-Url-Local.md](./issues/ISSUE-F3-01-001-Guard-Producao-Url-Local.md) |

## Artifact Minimo do Epico

- Guard em codigo
- Teste em `backend/tests/`

## Dependencias

- [Intake](../INTAKE.md)
- [PRD](../PRD-QR-GEN.md)
- [Fase](./F3_QR-GEN_EPICS.md)
- [F2](../F2-Migracao-Dados-Validacao/F2_QR-GEN_EPICS.md) — concluida
