# Dashboard de Leads

Status: backend MVP implementado.

## Endpoint
- `GET /dashboard/leads`

## Autenticacao
- Requer token Bearer (mesmo padrao das rotas autenticadas).

## Query params (MVP)
| Param | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| data_inicio | date (YYYY-MM-DD) | nao | Filtra por Lead.data_criacao >= data_inicio |
| data_fim | date (YYYY-MM-DD) | nao | Filtra por Lead.data_criacao <= data_fim |
| evento_id | int | nao | Filtra por Evento.id (via Ativacao -> AtivacaoLead) |
| evento_nome | string | nao | **Deprecated**: fallback temporario para filtrar por Evento.nome (case-insensitive) |
| estado | string | nao | UF (case-insensitive) do Evento |
| cidade | string | nao | Cidade (case-insensitive) do Evento |
| limit | int | nao | Top N para rankings (default=10, max=100) |
| granularity | day|month | nao | Serie temporal; se omitido: day ate 31 dias, senao month |

## Regras
- Os dados sao agregados a partir de Lead -> AtivacaoLead -> Ativacao -> Evento.
- Para usuario do tipo agencia, a visibilidade e limitada aos eventos da propria agencia.
- O endpoint retorna apenas agregados (sem expor email/telefone de leads).

## Response (v1)
```
{
  "version": 1,
  "generated_at": "2026-02-04T12:34:56+00:00",
  "filters": {
    "data_inicio": "2026-01-01",
    "data_fim": "2026-01-31",
    "evento_id": 123,
    "evento_nome": null,
    "estado": "SP",
    "cidade": "sao paulo",
    "limit": 10,
    "granularity": "day"
  },
  "kpis": {
    "leads_total": 120,
    "eventos_total": 4,
    "ativacoes_total": 12
  },
  "series": {
    "granularity": "day",
    "leads": [
      {"periodo": "2026-01-05", "total": 12},
      {"periodo": "2026-01-06", "total": 18}
    ]
  },
  "rankings": {
    "por_estado": [
      {"estado": "SP", "total": 50},
      {"estado": "RJ", "total": 30}
    ],
    "por_cidade": [
      {"cidade": "sao paulo", "total": 40},
      {"cidade": "rio", "total": 20}
    ],
    "por_evento": [
      {"evento_id": 123, "evento_nome": "Evento SP", "total": 25}
    ]
  }
}
```

## Observacoes de MVP
- Se algum detalhe nao estiver nos dados atuais, o campo nao e exposto.
- A definicao de conversoes/funil/fonte depende de modelos ainda nao presentes.
