# DOCX Como Spec de Dados

Este arquivo transforma o documento modelo de fechamento em um checklist de requisitos de dados. A intencao e que cada item abaixo vire um ou mais campos/tabelas no banco, com regras de calculo e linhagem para as fontes.

## Checklist (Contrato de Dados)

| Secao (DOCX) | Metrica/Conteudo esperado | Granularidade (evento/dia/sessao) | Tabelas/campos necessarios | Fonte atual no DOCX | Status |
|---|---|---|---|---|---|
| Contexto do evento | TODO | TODO | TODO | Secao "Contexto do evento" (template DOCX) | GAP |
| Publico por sessao | TODO | TODO | TODO | Secao "Publico por sessao" (template DOCX) | GAP |
| Shows por dia (12/12, 13/12, 14/12) | Para cada dia com show: entradas validadas, ingressos vendidos, opt-in aceitos e reconciliacao entre metricas | Dia e sessao (show) | `event_sessions` (tipo=show), `attendance_access_control`, `ticket_sales`, `optin_transactions` | Requisito obrigatorio de governanca (feedback de cobertura) | GAP |

## Figuras e Tabelas (Inventario do DOCX)

### Figuras (titulos)

- Entradas validadas por dia.

### Tabelas

- Publico por sessao: Campos esperados: `Metrica`, `Dia`, `Valor`.
