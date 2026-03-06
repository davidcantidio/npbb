---
doc_id: "EPIC-F2-02-ENDPOINTS-PREVIEW-COMMIT"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# EPIC-F2-02 - Endpoints Preview Commit

## Objetivo

Expor `POST /leads/import/etl/preview` e `POST /leads/import/etl/commit` no router `backend/app/routers/leads.py`, mantendo os endpoints legados de importacao intactos.

## Resultado de Negocio Mensuravel

O usuario consegue revisar qualidade de dados, confirmar warnings de forma explicita e persistir apenas o lote aprovado, reduzindo retrabalho operacional e carga incorreta no banco.

## Definition of Done

- O router `leads` publica os endpoints ETL com autenticacao, payloads e codigos de erro consistentes com o backend atual.
- `preview` devolve `session_token`, contagens e `dq_report` sem persistir definitivamente o lote.
- `commit` usa `session_token` e `force_warnings` para governar a persistencia do preview aprovado.
- Os endpoints legados `/leads/import/preview`, `/leads/import/validate` e `/leads/import` continuam sem regressao contratual.

## Issues

### ISSUE-F2-02-01 - Expor POST /leads/import/etl/preview
Status: todo

**User story**
Como pessoa que importa leads fora do padrao, quero um endpoint de preview ETL para revisar a qualidade do lote antes de confirmar a carga.

**Plano TDD**
1. `Red`: ampliar `backend/tests/test_lead_import_preview_xlsx.py` para falhar quando `backend/app/routers/leads.py` nao retornar `session_token`, contagens e `dq_report` no preview ETL.
2. `Green`: adicionar `POST /leads/import/etl/preview` ao router `leads`, recebendo `multipart/form-data` com `file`, `evento_id` e `strict=false`, e delegando ao use case ETL.
3. `Refactor`: padronizar validacao de payload, serializacao de erro e adaptacao do retorno para ficar alinhado ao restante do router.

**Criterios de aceitacao**
- Given upload autenticado com `file` e `evento_id`, When o endpoint responde, Then retorna `session_token`, `total_rows`, `valid_rows`, `invalid_rows` e `dq_report`.
- Given arquivo invalido, When o endpoint falha, Then `status`, `code` e `message` seguem o padrao do router atual.

### ISSUE-F2-02-02 - Expor POST /leads/import/etl/commit
Status: todo

**User story**
Como pessoa que aprovou um preview, quero um endpoint de commit ETL para persistir somente o lote revisado, com override explicito para warnings.

**Plano TDD**
1. `Red`: ampliar `backend/tests/test_leads_import_csv_smoke.py` para falhar quando `backend/app/routers/leads.py` nao respeitar `session_token` e `force_warnings` no commit ETL.
2. `Green`: adicionar `POST /leads/import/etl/commit` ao router `leads`, recebendo `session_token`, `evento_id` e `force_warnings=false`, e delegando a persistencia ao use case ETL.
3. `Refactor`: separar validacao de sessao, gate de warnings e serializacao de resposta para manter o endpoint curto e previsivel.

**Criterios de aceitacao**
- Given `session_token` valido e `force_warnings=false`, When so existem warnings, Then o commit continua bloqueado ate confirmacao explicita.
- Given `force_warnings=true` e ausencia de erros, When o commit executa, Then apenas linhas aprovadas sao persistidas.

### ISSUE-F2-02-03 - Preservar compatibilidade do router legado
Status: todo

**User story**
Como pessoa que depende do fluxo atual de importacao, quero que o router ETL conviva com os endpoints legados para evitar regressao na operacao corrente.

**Plano TDD**
1. `Red`: ampliar `backend/tests/test_lead_import_preview_xlsx.py`, `backend/tests/test_leads_import_csv_smoke.py` e os contratos consumidos por `frontend/src/services/leads_import.ts` para falhar diante de qualquer regressao nos endpoints legados.
2. `Green`: integrar os endpoints ETL ao router `leads` sem alterar paths, payloads ou autenticacao de `/leads/import/preview`, `/leads/import/validate` e `/leads/import`.
3. `Refactor`: consolidar helpers compartilhados de autenticacao e erro para que os fluxos legado e ETL usem a mesma infraestrutura sem acoplamento indevido.

**Criterios de aceitacao**
- Given os endpoints legados `/leads/import/preview`, `/leads/import/validate` e `/leads/import`, When o novo router ETL entra, Then esses contratos nao mudam.
- Given autenticacao BB atual, When `preview` e `commit` ETL sao chamados, Then o comportamento de auth e coerente com o restante do router `leads`.

## Artifact Minimo do Epico

- `artifacts/phase-f2/epic-f2-02-endpoints-preview-commit.md` com evidencias de resposta HTTP, erros padronizados e compatibilidade com o fluxo legado.

## Dependencias

- [PRD](../PRD-LEAD-ETL-FUSION.md)
- [SCRUM-GOV](../SCRUM-GOV.md)
- [DECISION-PROTOCOL](../DECISION-PROTOCOL.md)
