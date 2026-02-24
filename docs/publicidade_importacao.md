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
- `data_vinculacao` (obrigatorio)
- `meio` (obrigatorio)
- `veiculo` (obrigatorio)
- `uf` (obrigatorio)
- `uf_extenso` (opcional)
- `municipio` (opcional)
- `camada` (obrigatorio)

## Regras principais
- Chave natural da tabela final: `codigo_projeto + data_vinculacao + meio + veiculo + uf + camada`.
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

