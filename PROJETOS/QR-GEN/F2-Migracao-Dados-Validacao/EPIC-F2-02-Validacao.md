---
doc_id: "EPIC-F2-02-Validacao.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
---

# EPIC-F2-02 - Validacao

## Objetivo

Criar teste de validacao que garante zero registros com localhost apos migracao em ambiente de staging/producao.

## Resultado de Negocio Mensuravel

Metrica de sucesso: zero QR codes com URL de localhost persistidos no banco apos migracao.

## Contexto Arquitetural

- Tabela `ativacao` — colunas `landing_url`, `qr_code_url`, `url_promotor`
- Integracao com script de migracao da ISSUE-F2-01-001

## Definition of Done do Epico
- [ ] Teste de validacao executavel
- [ ] Cobertura de cenario pos-migracao

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F2-02-001 | Validacao Zero Localhost | Teste que valida zero registros com localhost apos migracao | 3 | todo | [ISSUE-F2-02-001-Validacao-Zero-Localhost.md](./issues/ISSUE-F2-02-001-Validacao-Zero-Localhost.md) |

## Artifact Minimo do Epico

- Teste automatizado em `backend/tests/` ou script de validacao

## Dependencias

- [Intake](../INTAKE.md)
- [PRD](../PRD-QR-GEN.md)
- [Fase](./F2_QR-GEN_EPICS.md)
- [EPIC-F2-01](./EPIC-F2-01-Migracao.md) — migracao executada
