# Requirements to Schema Mapping

Documento gerado automaticamente a partir do checklist do DOCX e do mapping YAML. Nao inclui conteudo manual nem metricas inventadas.

- `schema_version`: `1.0`
- `spec_source`: `docs/analises/eventos/tamo_junto_2025/planning/00_docx_as_spec.md`

## Mapeamento Item -> Campo -> Regra

| Requirement ID | Item (DOCX) | Tabela.campo | Regra de calculo | Fonte(s) | Validacoes | Observacoes (regua de publico) |
|---|---|---|---|---|---|---|
| REQ-SHOWS-DIA-001 | Shows por dia (12/12, 13/12, 14/12) | public.mart_report_show_day_summary.coverage_status | CASE WHEN has_access_control AND has_ticket_sales THEN 'OK' ELSE 'GAP' END | pdf_access_control_2025_12_12 (pagina 2 / tabela Entradas validadas); xlsx_optin_aceitos_2025_12 (aba Vendas / colunas data_compra,sessao) | VAL-SHOW-COVERAGE-001 [reconciliation/error] coverage_status IN ('OK','GAP','INCONSISTENTE') | Regua de publico: opt-in aceitos; Regua de publico: ingressos vendidos |
| REQ-PUBLICO-001 | Publico do evento (controle de acesso - entradas validadas) | public.attendance_access_control.entries_validated | SUM(entries_validated) por evento_dia_sessao | pdf_access_control_2025_12_13 (pagina 1 / tabela Presencas) | VAL-PUBLICO-NOT-NULL-001 [not_null/error] entries_validated IS NOT NULL | Regua de publico: entradas validadas |

## Cobertura do Checklist

| Item do checklist | Cobertura de mapping |
|---|---|
| Publico do evento (controle de acesso - entradas validadas) | OK |
| Shows por dia (12/12, 13/12, 14/12) | OK |
| Contexto do evento | GAP |
| Objetivo do relatorio | GAP |
| Fontes de dados e limitacoes | GAP |
| Big numbers (recorte analisado) | GAP |
| Dinamica de vendas (pre-venda) - shows (Opt-in aceitos) | GAP |
| Quem sao clientes do Banco (proxy via categoria de ingresso - Opt-in) | GAP |
| Perfil do publico (DIMAC - 12 a 14/12) | GAP |
| Satisfacao e percepcao (DIMAC) | GAP |
| Pre-venda (leitura tecnica e aprendizados) | GAP |
| Performance nas redes (Instagram e social listening) | GAP |
| Midia e imprensa (MTC) | GAP |
| Leads e ativacoes (Festival de Esportes | 12-14/12) | GAP |
| Recomendacoes (2026) - acoes tecnicas e de produto | GAP |
| Apendice - definicoes rapidas | GAP |

## Contratos de Mart

| Mart | Grain | Requirement IDs | Campos de saida |
|---|---|---|---|
| mart_report_show_day_summary | evento_dia_sessao | REQ-SHOWS-DIA-001, REQ-PUBLICO-001 | event_date, coverage_status |
