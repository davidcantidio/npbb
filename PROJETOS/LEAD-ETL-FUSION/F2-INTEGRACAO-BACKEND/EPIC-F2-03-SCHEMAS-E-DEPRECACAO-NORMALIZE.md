---
doc_id: "EPIC-F2-03-SCHEMAS-E-DEPRECACAO-NORMALIZE"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# EPIC-F2-03 - Schemas e Deprecacao Normalize

## Objetivo

Criar `backend/app/schemas/lead_import_etl.py` com os contratos `DQCheckResult`, `ImportEtlPreviewResponse` e `ImportEtlResult`, e marcar `backend/app/utils/lead_import_normalize.py` como deprecated em favor de `core/leads_etl/transform/column_normalize`.

## Resultado de Negocio Mensuravel

Backend e frontend passam a trocar payloads ETL previsiveis e versionaveis, enquanto o caminho legado de normalizacao fica claramente marcado para remocao controlada sem ambiguidade de fonte canonica.

## Definition of Done

- Os schemas ETL do backend cobrem preview, resultados de checks e retorno de commit com nomes e tipos estaveis.
- O frontend consegue consumir o contrato ETL sem adaptadores improvisados de campo.
- `lead_import_normalize.py` fica identificado como compatibilizador temporario, apontando para o core como fonte canonica.
- Guardrails de higiene ajudam a impedir novos acoplamentos ao helper legado.

## Issues

### ISSUE-F2-03-01 - Criar schemas ETL do backend
Status: todo

**User story**
Como pessoa que integra backend e frontend, quero schemas ETL explicitos para serializar preview e commit com o mesmo contrato em todos os ambientes.

**Plano TDD**
1. `Red`: ampliar `backend/tests/test_lead_import_preview_xlsx.py` e `backend/tests/test_leads_import_csv_smoke.py` para falhar quando a resposta ETL nao aderir a schemas nomeados em `backend/app/schemas/lead_import_etl.py`.
2. `Green`: criar `backend/app/schemas/lead_import_etl.py` com `DQCheckResult`, `ImportEtlPreviewResponse` e `ImportEtlResult`, integrando-os ao router ETL.
3. `Refactor`: alinhar nomes, tipos e defaults com `backend/app/schemas/lead_import.py` para reduzir sobreposicao e facilitar manutencao.

**Criterios de aceitacao**
- Given a resposta de preview ETL, When serializada, Then usa `ImportEtlPreviewResponse` com `dq_report: list[DQCheckResult]`.
- Given a resposta de commit ETL, When serializada, Then usa `ImportEtlResult` com contagens coerentes e prontas para consumo do frontend.

### ISSUE-F2-03-02 - Alinhar serializacao backend e frontend
Status: todo

**User story**
Como pessoa que mantem a UI de leads, quero que o payload ETL chegue com nomes e tipos estaveis para evitar adaptacoes ad hoc no service layer.

**Plano TDD**
1. `Red`: ampliar `frontend/src/services/leads_import.ts` e `frontend/src/features/leads-import/hooks/useLeadImportUpload.ts` para falhar quando o payload ETL exigir transformacao manual nao prevista.
2. `Green`: alinhar `backend/app/routers/leads.py` e os novos schemas ETL para que o frontend possa introduzir `previewLeadImportEtl` e `commitLeadImportEtl` com tipagem direta.
3. `Refactor`: consolidar testes de contrato entre backend e frontend para detectar drift de nomes, nulos e tipos.

**Criterios de aceitacao**
- Given o payload ETL do backend, When consumido pelo frontend, Then nomes de campo e tipos nao exigem adaptacao ad hoc.
- Given alteracao futura no schema, When os testes de contrato rodam, Then o drift e detectado antes de quebrar a UI.

### ISSUE-F2-03-03 - Marcar lead_import_normalize.py como deprecated
Status: todo

**User story**
Como pessoa mantenedora do backend, quero sinalizar o normalize legado como deprecated para impedir que novas features o adotem como fonte de verdade.

**Plano TDD**
1. `Red`: ampliar `backend/tests/test_leads_import_csv_smoke.py` e os checks de `scripts/check_repo_hygiene.sh` para falhar quando o helper legado voltar a ser tratado como implementacao canonica.
2. `Green`: adicionar comentario canonicamente padronizado em `backend/app/utils/lead_import_normalize.py` apontando para `core/leads_etl/transform/column_normalize`.
3. `Refactor`: ajustar a higiene do repositorio para tornar explicito que novos imports diretos do helper legado sao regressao arquitetural.

**Criterios de aceitacao**
- Given o helper legado, When consultado apos a F2, Then ele contem comentario canonico apontando para `core/leads_etl/transform/column_normalize`.
- Given novos imports diretos para esse helper, When o hygiene check roda, Then a regressao e detectada de forma objetiva.

## Artifact Minimo do Epico

- `artifacts/phase-f2/epic-f2-03-schemas-e-deprecacao-normalize.md` com contratos ETL publicados, alinhamento de serializacao e evidencias de deprecacao controlada.

## Dependencias

- [PRD](../PRD-LEAD-ETL-FUSION.md)
- [SCRUM-GOV](../SCRUM-GOV.md)
- [DECISION-PROTOCOL](../DECISION-PROTOCOL.md)
