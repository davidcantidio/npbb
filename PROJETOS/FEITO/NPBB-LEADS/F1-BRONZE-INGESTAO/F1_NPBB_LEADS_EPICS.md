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

- [x] `POST /leads/batches` operacional com JWT e persistencia `arquivo_bronze`
- [x] `GET /leads/batches/{id}/preview` retornando colunas + amostra de linhas
- [x] Frontend com rota unica de importacao (`/leads/importar`) em fluxo de 2 passos
- [x] Rota antiga de importacao avancada redirecionada para rota unificada
- [x] Navegacao para mapeamento preparada com `batch_id` (handoff para F2)

## Epics da Fase

| Epic ID | Nome | Objetivo | Status | Documento |
|---------|------|----------|--------|------------|
| `EPIC-F1-01` | Upload e Registro Bronze | Implementar upload e persistência de dados brutos na camada Bronze. | ✅ | [EPIC-F1-01-UPLOAD-E-REGISTRO-BRONZE.md](./EPIC-F1-01-UPLOAD-E-REGISTRO-BRONZE.md) |
| `EPIC-F1-02` | Unificação UI Importação | Unificar a interface de importação de leads. | ✅ | [EPIC-F1-02-UNIFICACAO-UI-IMPORTACAO.md](./EPIC-F1-02-UNIFICACAO-UI-IMPORTACAO.md) |
