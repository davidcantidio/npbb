# Importacao Assistida de Publicidade (CSV/XLSX)

## Objetivo
Aplicar o fluxo assistido (preview -> sugestao -> validacao -> import) no dominio de publicidade, reutilizando o core generico de importacao.

## Endpoints
- `POST /publicidade/import/upload`  
  Valida extensao e tamanho do arquivo.
- `POST /publicidade/import/preview`  
  Retorna `headers`, `rows`, `start_index`, `suggestions`, `samples_by_column`, `alias_hits`.
- `POST /publicidade/import/validate`  
  Valida o mapeamento por dominio.
- `POST /publicidade/import`  
  Executa import com `mappings_json` e suporte a `dry_run`.
- `GET /publicidade/referencias/eventos`  
  Lista eventos com `id`, `nome`, `external_project_code`.
- `GET /publicidade/aliases` e `POST /publicidade/aliases`  
  Lookup/persistencia de alias generico por dominio.

## Campos do dominio
- `codigo_projeto` (obrigatorio)
- `projeto` (obrigatorio)
- `data_veiculacao` (obrigatorio)
- `meio` (obrigatorio)
- `veiculo` (obrigatorio)
- `uf` (obrigatorio)
- `uf_extenso` (opcional)
- `municipio` (opcional)
- `camada` (obrigatorio)

## Regras principais
- Chave natural da tabela final: `codigo_projeto + data_veiculacao + meio + veiculo + uf + camada`.
- Normalizacao:
  - `UF`, `Meio`, `Camada` e `Codigo projeto` em uppercase.
  - data aceita `DD/MM/YYYY` e `YYYY-MM-DD`.
- Idempotencia:
  - staging deduplicado por `source_file + source_row_hash`.
  - final deduplicado por chave natural (upsert).
- Resolucao de evento:
  - prioridade para `evento.external_project_code`.
  - fallback por alias de `codigo_projeto` (domain=`publicidade`).
- `dry_run=true` valida e calcula relatorio sem persistir dados.

## Contrato do relatorio
- `received_rows`
- `valid_rows`
- `staged_inserted`
- `staged_skipped`
- `upsert_inserted`
- `upsert_updated`
- `unresolved_event_id`
- `errors` (lista estruturada por linha/campo)

## Escalabilidade por dominio
O pipeline foi implementado sobre um core reutilizavel em `backend/app/services/imports/`:
- leitura padrao CSV/XLSX;
- sugestao de mapeamento por heuristica;
- validacao de mapeamento por dominio;
- alias generico por dominio/campo.

Esse mesmo padrao pode ser replicado para outros dominios (ex.: `evento/import/csv`) sem refatoracao destrutiva.

## Validacao operacional (smoke API)
Objetivo:
- validar rapidamente se o backend ativo possui as rotas de publicidade;
- reproduzir e isolar falhas de ambiente (ex.: `Not Found` por backend stale);
- executar importacao real minima e checar idempotencia.

### 1) Padronizar runtime local
PowerShell:
```powershell
# encerra listeners de 8000/8001 (se existirem)
$ports = 8000, 8001
Get-NetTCPConnection -State Listen -LocalPort $ports -ErrorAction SilentlyContinue |
  Select-Object -ExpandProperty OwningProcess -Unique |
  ForEach-Object { Stop-Process -Id $_ -Force }

# backend canonico
Set-Location npbb\backend
python -m uvicorn app.main:app --reload --port 8000
```

Em outro terminal:
```powershell
Set-Location npbb\frontend
$env:VITE_API_BASE_URL = "http://localhost:8000"
npm run dev -- --port 5173
```

### 2) Rodar smoke de publicidade (MCP equivalente)
PowerShell:
```powershell
Set-Location npbb\backend
$env:NPBB_BASE_URL = "http://localhost:8000"
$env:NPBB_TEST_EMAIL = "seu.email@dominio"
$env:NPBB_TEST_PASSWORD = "sua_senha"
$env:NPBB_SMOKE_TIMEOUT_SEC = "20"
python -m scripts.smoke_publicidade_import
```

Saidas esperadas:
- resumo no stdout com `preview`, `validate`, `import_first` e `import_second`;
- arquivo JSON em `reports/publicidade_smoke/<timestamp>.json`.

## Diagnostico rapido de falhas
- `404` em `/publicidade/*`: backend errado/stale em runtime (processo antigo ou checkout antigo).
- `401`: token ausente/expirado ou credencial invalida.
- `400`/`422`: arquivo invalido, mapeamento incompleto ou tipo de dado invalido.

## Seguranca operacional
- use credenciais apenas por variaveis de ambiente (`NPBB_TEST_EMAIL`, `NPBB_TEST_PASSWORD`);
- nao hardcode token/senha em scripts;
- o smoke nao imprime token nem senha em log.

