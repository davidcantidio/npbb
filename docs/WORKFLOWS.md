# Workflows principais

## 1) Importacao de Leads (CSV/XLSX)
### UI
1. Faca login.
2. Acesse `/leads`.
3. Clique em **Importar XLSX** e selecione um arquivo `.csv` ou `.xlsx`.
4. Revise o **mapeamento de colunas**.
5. Ajuste referencias (evento/cidade/estado/genero) quando houver sugestoes.
6. Clique em **Importar**.
7. Consulte a tabela **Leads cadastrados** (paginada) na mesma tela.

### Tabela de leads na UI (`/leads`)
- Fonte de dados: `GET /leads?page=<n>&page_size=<n>`.
- Colunas principais exibidas:
  - Nome, email, telefone, CPF
  - Evento (origem): `evento_nome`, `cidade`, `estado`
  - Evento convertido: `evento_convertido_nome` (ou `evento_convertido_id`)
  - Conversao: `tipo_conversao`, `data_conversao`
  - Datas: `data_compra`, `data_criacao`
- Ao concluir um import, a listagem e recarregada automaticamente (volta para pagina 1).

### API (pipeline)
Endpoints principais:
- `GET /leads` (query: `page`, `page_size`)  
  Lista leads com paginacao e dados da conversao mais recente por lead.
- `POST /leads/import/preview` (multipart)  
  Retorna headers, amostra e sugestoes de mapeamento.
- `POST /leads/import/validate` (JSON)  
  Valida o mapeamento.
- `POST /leads/import` (multipart)  
  Executa o import.

Endpoints auxiliares:
- `GET /leads/referencias/eventos|cidades|estados|generos`
- `GET /leads/aliases` e `POST /leads/aliases` (aliases de referencia)

Exemplo (preview):
```bash
curl -X POST http://localhost:8000/leads/import/preview \
  -H "Authorization: Bearer <token>" \
  -F "file=@/caminho/arquivo.xlsx" \
  -F "sample_rows=10"
```

## 2) Importacao de Publicidade (CSV/XLSX)
### UI
1. Faca login.
2. Acesse `/publicidade`.
3. Clique em **Importar CSV/XLSX**.
4. Revise as sugestoes e ajuste mapeamentos.
5. (Opcional) confirme alias de `codigo_projeto`.
6. Execute import normal ou `dry-run`.

### API (pipeline)
Endpoints principais:
- `POST /publicidade/import/upload` (multipart)
- `POST /publicidade/import/preview` (multipart)
- `POST /publicidade/import/validate` (JSON)
- `POST /publicidade/import` (multipart; `mappings_json` + `dry_run`)

Endpoints auxiliares:
- `GET /publicidade/referencias/eventos`
- `GET /publicidade/aliases` e `POST /publicidade/aliases`

Relatorio esperado:
- `received_rows`, `valid_rows`
- `staged_inserted`, `staged_skipped`
- `upsert_inserted`, `upsert_updated`
- `unresolved_event_id`, `errors`

### Smoke API (MCP equivalente)
Use o script para validar login + preview + validate + import real + reimport idempotente:
```powershell
Set-Location npbb\backend
$env:NPBB_BASE_URL = "http://localhost:8000"
$env:NPBB_TEST_EMAIL = "seu.email@dominio"
$env:NPBB_TEST_PASSWORD = "sua_senha"
$env:NPBB_SMOKE_TIMEOUT_SEC = "20"
python -m scripts.smoke_publicidade_import
```

Artefatos:
- stdout com resumo das assercoes;
- `reports/publicidade_smoke/<timestamp>.json`.

Diagnostico rapido:
- `404` em `/publicidade/*` => backend stale/errado em runtime.
- `401` => problema de autenticacao/token.
- `400`/`422` => arquivo/mapeamento invalido.

## 3) Dashboard de Leads
### UI
- Rota: `/dashboard/leads`
- Mostra KPIs, serie temporal e rankings agregados.

### API
- `GET /dashboard/leads`  
  Filtros: `data_inicio`, `data_fim`, `evento_id`, `evento_nome` (fallback), `estado`, `cidade`, `limit`, `granularity`.

- `GET /dashboard/leads/relatorio`  
  Filtros: `evento_id` (preferencial) ou `evento_nome`, `data_inicio`, `data_fim`.

Exemplo:
```bash
curl "http://localhost:8000/dashboard/leads?evento_id=123&data_inicio=2025-01-01&data_fim=2025-12-31" \
  -H "Authorization: Bearer <token>"
```

## 4) Relatorio TMJ 2025 (DOCX)
Script oficial:
```bash
cd backend
python scripts/generate_tmj_report.py \
  --evento-nome "Festival TMJ 2025" \
  --data-inicio 2025-01-01 \
  --data-fim 2025-12-31
```

Saida:
- `reports/Festival_TMJ_2025_relatorio.docx`

Observacoes:
- O script usa o mesmo service do dashboard e gera apenas dados agregados.
- Se faltarem dados (ex.: redes sociais), o relatorio inclui a lacuna.

## 5) TMJ 2025 Dry-Run (ETL -> DQ -> Coverage -> Word)
Script:
```bash
python scripts/dry_run_tmj_pipeline.py --out-dir reports/tmj2025/dry_run
```

Objetivo:
- Validar localmente o encadeamento completo com fixtures, sem depender de banco externo ou fontes reais.

Fluxo executado:
- Extractors de fixtures (`xlsx`, `pdf`, `pptx`).
- Seed de banco local SQLite (`sources`, `ingestions`, `event_sessions` via agenda).
- Preflight (`dq:run` + coverage por sessao/show).
- Render do DOCX com gate e geracao de manifest.

Artefatos gerados:
- `reports/tmj2025/dry_run/dq_report.json`
- `reports/tmj2025/dry_run/coverage_report.json`
- `reports/tmj2025/dry_run/report.docx`
- `reports/tmj2025/dry_run/manifest.json`

Observacoes:
- O dry-run usa fixtures locais em `tests/fixtures`.
- O banco do dry-run e isolado em `reports/tmj2025/dry_run/dry_run.sqlite`.
- Guia detalhado: `docs/etl/tmj2025_dry_run_usage.md`.

## 6) Ingestao Inteligente S1 (Upload + Selecao de Evento)
### API
Endpoints internos da sprint:
- `POST /internal/ingestao-inteligente/s1/scaffold`
- `POST /internal/ingestao-inteligente/s1/upload`

Contrato operacional (resumo):
- Entrada: `evento_id`, `nome_arquivo`, `tamanho_arquivo_bytes`, `content_type`, `correlation_id` (opcional).
- Saida scaffold: limites de upload + `pontos_integracao` + `observabilidade`.
- Saida upload: `upload_id`, `status=accepted`, `proxima_acao`, `observabilidade`.

Observabilidade:
- Todos os erros retornam `code`, `message`, `action`, `correlation_id`, `telemetry_event_id`.
- Sucesso e erro geram eventos estruturados no logger `app.telemetry`.
- O frontend S1 mantem rastreabilidade por `observability_event_id` e propaga `correlation_id`.
