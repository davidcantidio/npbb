# EPIC-F1-01 — Upload e Registro Bronze
**projeto:** NPBB-LEADS | **fase:** F1 | **status:** ✅

## 1. Resumo
Criar o modelo `LeadBatch`, a migration Alembic e o endpoint POST /leads/batches
que recebe um arquivo CSV/XLSX, salva o arquivo bruto no banco (bytea) e registra
quem enviou, de qual plataforma e em que data.

## 2. Contexto Arquitetural
- Modelos em `backend/app/models/` (SQLModel)
- Routers em `backend/app/routers/`
- PYTHONPATH: `/workspace:/workspace/backend`
- Testes com `TESTING=true` (SQLite)
- Arquivo bruto: salvar como `bytea` no Postgres por ora (storage externo é fase futura)

## 3. Riscos
- Arquivos grandes (>10MB): usar `UploadFile` do FastAPI com streaming
- Não quebrar a rota GET /leads existente

## 4. Definition of Done
- [x] Model `LeadBatch` em `backend/app/models/lead_batch.py`
- [x] Migration Alembic gerada e aplicável
- [x] POST /leads/batches implementado e testado
- [x] Endpoint retorna 401 sem JWT

---
## Issues

### NPBB-F1-01-001 — Model LeadBatch + Migration
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** ✅
**depende de:** nenhuma

**Descrição:**
Criar o SQLModel `LeadBatch` com os campos definidos no PRD (seção Modelo de
Dados), gerar a migration Alembic e validar aplicação no banco local.

**Critérios de Aceitação:**
- [x] Classe `LeadBatch` em `backend/app/models/lead_batch.py`
- [x] Enum `BatchStage` com valores: bronze, silver, gold
- [x] `alembic upgrade head` aplica sem erro
- [x] `alembic downgrade -1` reverte sem erro

**Tarefas:**
- [x] T1: Criar `backend/app/models/lead_batch.py` com SQLModel + campos do PRD
- [x] T2: Criar `backend/app/models/lead_column_alias.py`
- [x] T3: Criar `backend/app/models/lead_silver.py`
- [x] T4: Exportar novos modelos em `backend/app/models/__init__.py`
- [x] T5: Gerar migration: `alembic revision --autogenerate -m "add_lead_batch_silver_alias"`
- [x] T6: Testar `alembic upgrade head` e `downgrade -1`

---
### NPBB-F1-01-002 — Endpoint POST /leads/batches
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** ✅
**depende de:** NPBB-F1-01-001

**Descrição:**
Criar rota POST /leads/batches em `backend/app/routers/leads.py` que recebe
UploadFile + metadados de envio (plataforma_origem, data_envio), salva o arquivo
como bytea em `lead_batches.arquivo_bronze` e retorna o batch criado.

**Critérios de Aceitação:**
- [x] POST /leads/batches aceita multipart/form-data com arquivo + metadados
- [x] Arquivo salvo íntegro (bytes recuperáveis via GET /leads/batches/{id}/arquivo)
- [x] Retorna 401 sem JWT
- [x] Retorna batch_id, stage=bronze, pipeline_status=pending

**Tarefas:**
- [x] T1: Adicionar rota POST /leads/batches com UploadFile
- [x] T2: Salvar bytes do arquivo em `lead_batches.arquivo_bronze`
- [x] T3: Adicionar rota GET /leads/batches/{id}/arquivo para download do bruto
- [x] T4: Escrever pytest (upload CSV, upload XLSX, sem token → 401)

**Notas técnicas:**
`arquivo_bronze` como `LargeBinary` no SQLModel. Para testes, usar
`BytesIO` com conteúdo CSV sintético como fixture.