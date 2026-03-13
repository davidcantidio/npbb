---
doc_id: "ISSUE-F1-02-001-Documentar-Public-App-Base-Url.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-13"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F1-02-001 - Documentar Public App Base Url

## User Story

Como DevOps ou desenvolvedor, quero documentacao explicita sobre a obrigatoriedade de `PUBLIC_APP_BASE_URL` em producao e um checklist de deploy, para garantir configuracao correta no go-live.

## Contexto Tecnico

O modulo `backend/app/utils/urls.py` usa `get_public_app_base_url()` com ordem: `PUBLIC_APP_BASE_URL` > `FRONTEND_ORIGIN` > fallback `http://localhost:5173`. Em producao, a variavel deve estar configurada. Producao: `app.npbb.com.br`.

## Plano TDD

- Red: N/A (documentacao)
- Green: Documentacao clara e checklist completo
- Refactor: Revisao de clareza

## Criterios de Aceitacao

- Given que nao existe documentacao, When leio `docs/SETUP.md` e/ou `docs/DEPLOY_*.md`, Then encontro secao explicando obrigatoriedade de `PUBLIC_APP_BASE_URL` em producao
- Given o checklist de deploy, When executo pre-go-live, Then inclui verificacao dessa variavel para `app.npbb.com.br`
- Given ambiente de producao, When a variavel nao estiver configurada, Then a documentacao indica o risco (QR codes com URL incorreta)

## Definition of Done da Issue
- [x] Documentacao em `docs/SETUP.md` e/ou `docs/DEPLOY_*.md`
- [x] Checklist de deploy criado ou atualizado
- [x] PM e DevOps cientes

## Tasks Decupadas

- [x] T1: Adicionar secao em `docs/SETUP.md` ou criar `docs/DEPLOY_*.md` sobre `PUBLIC_APP_BASE_URL`
- [x] T2: Criar ou atualizar checklist de deploy para `app.npbb.com.br`
- [x] T3: Incluir verificacao da variavel no checklist

## Arquivos Reais Envolvidos

- `docs/SETUP.md`
- `docs/DEPLOY_*.md` (criar se nao existir)
- `backend/app/utils/urls.py` — referencia para documentacao

## Artifact Minimo

- Documentacao publicada em `docs/`
- Checklist de deploy com item de verificacao

## Dependencias

- [Intake](../../INTAKE.md)
- [Epic](../EPIC-F1-02-Documentacao.md)
- [Fase](../F1_QR-GEN_EPICS.md)
- [PRD](../../PRD-QR-GEN.md)
