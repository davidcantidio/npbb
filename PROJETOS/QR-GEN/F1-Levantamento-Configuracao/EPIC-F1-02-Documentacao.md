---
doc_id: "EPIC-F1-02-Documentacao.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
---

# EPIC-F1-02 - Documentacao

## Objetivo

Documentar a obrigatoriedade de `PUBLIC_APP_BASE_URL` em producao e criar checklist de deploy para `app.npbb.com.br`.

## Resultado de Negocio Mensuravel

PM e DevOps cientes da dependencia de configuracao; checklist de deploy disponivel para go-live.

## Contexto Arquitetural

- `backend/app/utils/urls.py` — `get_public_app_base_url()` usa `PUBLIC_APP_BASE_URL` ou `FRONTEND_ORIGIN`
- Producao: `app.npbb.com.br`

## Definition of Done do Epico
- [ ] Documentacao em `docs/SETUP.md` e/ou `docs/DEPLOY_*.md`
- [ ] Checklist de deploy criado

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-02-001 | Documentar Public App Base Url | Documentacao e checklist de deploy | 3 | todo | [ISSUE-F1-02-001-Documentar-Public-App-Base-Url.md](./issues/ISSUE-F1-02-001-Documentar-Public-App-Base-Url.md) |

## Artifact Minimo do Epico

- Secao ou arquivo em `docs/` com instrucoes de configuracao
- Checklist de deploy para `app.npbb.com.br`

## Dependencias
- [Intake](../INTAKE.md)
- [PRD](../PRD-QR-GEN.md)
- [Fase](./F1_QR-GEN_EPICS.md)
- [EPIC-F1-01](./EPIC-F1-01-Levantamento.md) — volume documentado informa prioridade
