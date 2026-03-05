---
doc_id: "F1-NPBB-LEADS-EPICS"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-05"
---

# F1 Bronze Ingestão — Epics

## Objetivo da Fase

Implementar a camada Bronze de ingestão de leads: upload de arquivos e registro dos dados brutos.

## Gate de Saída da Fase

- [x] Modelos `LeadBatch`, `LeadColumnAlias`, `LeadSilver` criados e migrados
- [x] `POST /leads/batches` e `GET /leads/batches/{id}/arquivo` operacionais (retorna 401 sem JWT)
- [x] `GET /leads/batches/{id}/preview` retorna colunas + 3 linhas de amostra
- [x] UI de importação unificada com Stepper Bronze (Step1 + Step2)
- [x] Aba "Importação Avançada" removida
- [x] 289 testes backend passam (3 falhas pré-existentes sem relação com F1)
- [x] 41 testes frontend passam

## Epics da Fase

| Epic ID | Nome | Objetivo | Status | Documento |
|---------|------|----------|--------|------------|
| `EPIC-F1-01` | Upload e Registro Bronze | Implementar upload e persistência de dados brutos na camada Bronze. | `done` ✅ | [EPIC-F1-01-UPLOAD-E-REGISTRO-BRONZE.md](./EPIC-F1-01-UPLOAD-E-REGISTRO-BRONZE.md) |
| `EPIC-F1-02` | Unificação UI Importação | Unificar a interface de importação de leads. | `done` ✅ | [EPIC-F1-02-UNIFICACAO-UI-IMPORTACAO.md](./EPIC-F1-02-UNIFICACAO-UI-IMPORTACAO.md) |
