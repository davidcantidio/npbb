---
doc_id: "EPIC-F3-02-Consolidar-Configuracao-Final-e-Remover-Dependencia-do-Postgres-Local.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-16"
---

# EPIC-F3-02 - Consolidar configuracao final e remover dependencia do Postgres local

## Objetivo

Atualizar os pontos de configuracao e documentacao do repositorio para refletir
o Supabase como banco unico do projeto, preservando somente o fallback de testes
em SQLite e eliminando o PostgreSQL local como requisito operacional padrao.

## Resultado de Negocio Mensuravel

- `DATABASE_URL` e `DIRECT_URL` ficam documentadas com o papel final de runtime e migrations
- setup e troubleshooting deixam de instruir o PostgreSQL local como caminho principal
- deploy e configuracao ficam coerentes com Render + Supabase

## Contexto Arquitetural

- `backend/.env.example` e a referencia primaria de variaveis de ambiente do backend
- `docs/SETUP.md`, `docs/TROUBLESHOOTING.md` e `docs/DEPLOY_RENDER_CLOUDFLARE.md` concentram o estado operacional esperado
- `docs/render.yaml` representa a configuracao de deploy do backend em producao

## Definition of Done do Epico
- [ ] configuracao e documentacao alinhadas ao Supabase como banco unico
- [ ] PostgreSQL local removido como requisito operacional padrao
- [ ] fallback SQLite de testes e contrato de deploy preservados

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F3-02-001 | Atualizar configuracao e documentacao para Supabase como banco unico | Consolidar o estado final de setup, troubleshooting e deploy apos a migracao | 3 | todo | [ISSUE-F3-02-001-Atualizar-Configuracao-e-Documentacao-para-Supabase-como-Banco-Unico.md](./issues/ISSUE-F3-02-001-Atualizar-Configuracao-e-Documentacao-para-Supabase-como-Banco-Unico.md) |

## Artifact Minimo do Epico

- configuracao e documentacao finais do backend refletindo Supabase como banco unico

## Dependencias
- [Intake](../INTAKE-SUPABASE.md)
- [PRD](../PRD-SUPABASE.md)
- [Fase](./F3_SUPABASE_EPICS.md)
- [EPIC-F3-01](./EPIC-F3-01-Validar-Backend-e-Scripts-Criticos-contra-Supabase.md)
