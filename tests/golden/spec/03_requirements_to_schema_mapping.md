# Requirements to Schema Mapping

Documento gerado automaticamente a partir do checklist do DOCX e do mapping YAML. Nao inclui conteudo manual nem metricas inventadas.

- `schema_version`: `1.0`
- `spec_source`: `docs/analises/eventos/tamo_junto_2025/planning/00_docx_as_spec.md`

## Mapeamento Item -> Campo -> Regra

| Requirement ID | Item (DOCX) | Tabela.campo | Regra de calculo | Fonte(s) | Validacoes | Observacoes (regua de publico) |
|---|---|---|---|---|---|---|
| REQ-PUBLICO-001 | Publico do evento (controle de acesso - entradas validadas) | public.attendance_access_control.entries_validated | SUM(entries_validated) por evento_dia_sessao | pdf_access_control_2025_12_13 (pagina 1 / tabela Presencas) | VAL-PUBLICO-001 [not_null/error] entries_validated IS NOT NULL | Regua de publico: entradas validadas |
| REQ-OPTIN-001 | Dinamica de vendas (pre-venda) - shows (Opt-in aceitos) | public.optin_transactions.optin_accepted | SUM(optin_accepted) por evento_dia_sessao | xlsx_optin_aceitos_2025_12 (aba Vendas / colunas data_compra,sessao) | VAL-OPTIN-001 [reconciliation/error] optin_accepted >= 0 | Regua de publico: opt-in aceitos; Regua de publico: ingressos vendidos |

## Cobertura do Checklist

| Item do checklist | Cobertura de mapping |
|---|---|
| Contexto do evento | GAP |
| Publico por sessao | GAP |
| Shows por dia (12/12, 13/12, 14/12) | GAP |

## Contratos de Mart

| Mart | Grain | Requirement IDs | Campos de saida |
|---|---|---|---|
| mart_report_show_day_summary | evento_dia_sessao | REQ-PUBLICO-001, REQ-OPTIN-001 | entries_validated, optin_accepted |
