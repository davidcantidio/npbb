# Workflows principais

## 1) Importacao de Leads (CSV/XLSX)
### UI
1. Faça login.
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

## 2) Dashboard de Leads
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

## 3) Relatorio TMJ 2025 (DOCX)
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
- O script usa o mesmo service do dashboard e gera **apenas dados agregados**.
- Se faltarem dados (ex.: redes sociais), o relatorio inclui a lacuna.
