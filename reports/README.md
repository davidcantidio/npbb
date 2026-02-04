# Relatorios e dashboard (TMJ 2025)

## Endpoints
- `GET /dashboard/leads` (agregado, sem PII)
- `GET /dashboard/leads/relatorio` (relatorio TMJ 2025)

### Parametros principais (relatorio)
- `evento_id` (preferencial) ou `evento_nome` (fallback, deprecated)
- `data_inicio` / `data_fim` (YYYY-MM-DD)

## Gerar DOCX (TMJ 2025)
Comandos:
```
$env:TESTING='true'
$env:PYTHONPATH='npbb/backend'
python npbb/backend/scripts/generate_tmj_report.py --evento-nome "Festival TMJ 2025"
```

Saida esperada:
- `npbb/reports/Festival_TMJ_2025_relatorio.docx`

## Dados necessarios
- Leads com `evento_nome` consistente (idealmente com `evento_id` no futuro).
- Datas de compra (`data_compra`) para pre-venda.
- `publico_realizado`/`publico_projetado` em Evento para publico do evento.
- Indicador de cliente BB (ainda nao existe).
- Metricas de redes (ainda nao existe).

## Limitacoes atuais
- Sem indicador de clientes BB no Lead (relatorio retorna 0 + aviso).
- Sem dados de redes sociais no sistema.
- Pre-venda depende de `data_inicio` do evento.
