# Dashboard de Leads

Status: backend MVP implementado.

## Rotas e endpoints
- UI atual: `/dashboard/leads/analise-etaria`
- Redirect de compatibilidade: `/dashboard/leads` -> `/dashboard/leads/analise-etaria`
- Sem tela roteada nesta fase: `/dashboard/leads/relatorio`

## Endpoint
- `GET /dashboard/leads`
- `GET /dashboard/leads/relatorio` (TMJ 2025)

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

---

## Relatorio agregado (TMJ 2025)

### Endpoint
- `GET /dashboard/leads/relatorio`

### Query params
| Param | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| evento_id | int | sim (ou evento_nome) | Preferencial; busca Evento e filtra leads por `Lead.evento_nome` (case-insensitive). |
| evento_nome | string | sim (ou evento_id) | Fallback; **deprecated** quando evento_id estiver disponivel em todos os fluxos. |
| data_inicio | date (YYYY-MM-DD) | nao | Filtra por data da compra (Lead.data_compra) ou data_criacao. |
| data_fim | date (YYYY-MM-DD) | nao | Filtra por data da compra (Lead.data_compra) ou data_criacao. |

### Regras
- Dados sempre agregados (sem PII).
- Para usuario de agencia, `evento_id` e obrigatorio.
- Se o evento nao existir, retorna 404.

### Response (v1 - exemplo)
```
{
  "version": 1,
  "generated_at": "2026-02-04T12:34:56+00:00",
  "filters": {
    "data_inicio": "2025-01-01",
    "data_fim": "2025-12-31",
    "evento_id": 84,
    "evento_nome": "festival tmj 2025"
  },
  "big_numbers": {
    "total_leads": 1200,
    "total_compras": 980,
    "total_publico": 15000,
    "taxa_conversao": 81.67,
    "criterio_publico": "evento.publico_realizado",
    "criterio_compras": "contagem_compras_por_data_compra"
  },
  "perfil_publico": {
    "distribuicao_idade": [
      {"faixa": "18-24", "total": 200, "percentual": 25.0}
    ],
    "distribuicao_genero": [
      {"faixa": "feminino", "total": 600, "percentual": 50.0}
    ],
    "percent_sem_idade": 10.0,
    "percent_sem_genero": 5.0
  },
  "clientes_bb": {
    "total_clientes_bb": 0,
    "percentual_clientes_bb": 0.0,
    "criterio_usado": "sem_dados_no_sistema"
  },
  "pre_venda": {
    "janela_pre_venda": "ate 2025-03-15",
    "volume_pre_venda": 300,
    "volume_venda_geral": 980,
    "observacao": "Pre-venda definida ate a data de inicio do evento."
  },
  "redes": {
    "status": "sem_dados",
    "observacao": "Sem dados de redes sociais no sistema.",
    "metricas": null
  },
  "dados_faltantes": [
    "Nao ha indicador de clientes BB nos leads.",
    "Nao ha dados de redes sociais no sistema."
  ]
}
```
