# DOCX Como Spec de Dados

Este arquivo transforma o documento modelo de fechamento em um checklist de requisitos de dados. A intencao e que cada item abaixo vire um ou mais campos/tabelas no banco, com regras de calculo e linhagem para as fontes.

## Checklist (Contrato de Dados)

| Secao (DOCX) | Metrica/Conteudo esperado | Granularidade (evento/dia/sessao) | Tabelas/campos necessarios | Fonte atual no DOCX | Status |
|---|---|---|---|---|---|
| Contexto do evento | TODO | TODO | TODO | Secao "Contexto do evento" (template DOCX) | GAP |
| Objetivo do relatorio | TODO | TODO | TODO | Secao "Objetivo do relatorio" (template DOCX) | GAP |
| Fontes de dados e limitacoes | TODO | TODO | TODO | Secao "Fontes de dados e limitacoes" (template DOCX) | GAP |
| Big numbers (recorte analisado) | TODO | TODO | TODO | Secao "Big numbers (recorte analisado)" (template DOCX) | GAP |
| Publico do evento (controle de acesso - entradas validadas) | TODO | TODO | TODO | Secao "Publico do evento (controle de acesso - entradas validadas)" (template DOCX) | GAP |
| Dinamica de vendas (pre-venda) - shows (Opt-in aceitos) | TODO | TODO | TODO | Secao "Dinamica de vendas (pre-venda) - shows (Opt-in aceitos)" (template DOCX) | GAP |
| Quem sao clientes do Banco (proxy via categoria de ingresso - Opt-in) | TODO | TODO | TODO | Secao "Quem sao clientes do Banco (proxy via categoria de ingresso - Opt-in)" (template DOCX) | GAP |
| Perfil do publico (DIMAC) | TODO | TODO | TODO | Secao "Perfil do publico (DIMAC)" (template DOCX) | GAP |
| Satisfacao e percepcao (DIMAC) | TODO | TODO | TODO | Secao "Satisfacao e percepcao (DIMAC)" (template DOCX) | GAP |
| Pre-venda (leitura tecnica e aprendizados) | TODO | TODO | TODO | Secao "Pre-venda (leitura tecnica e aprendizados)" (template DOCX) | GAP |
| Performance nas redes (Instagram e social listening) | TODO | TODO | TODO | Secao "Performance nas redes (Instagram e social listening)" (template DOCX) | GAP |
| Midia e imprensa (MTC) | TODO | TODO | TODO | Secao "Midia e imprensa (MTC)" (template DOCX) | GAP |
| Leads e ativacoes (Festival de Esportes) | TODO | TODO | TODO | Secao "Leads e ativacoes (Festival de Esportes)" (template DOCX) | GAP |
| Recomendacoes - acoes tecnicas e de produto | TODO | TODO | TODO | Secao "Recomendacoes - acoes tecnicas e de produto" (template DOCX) | GAP |
| Apendice - definicoes rapidas | TODO | TODO | TODO | Secao "Apendice - definicoes rapidas" (template DOCX) | GAP |
| Shows por dia (doze, treze, quatorze de dezembro) | Para cada dia com show: entradas validadas (controle de acesso), ingressos vendidos (total), opt-in aceitos e reconciliacao entre metricas | Dia e sessao (show) | `event_sessions` (tipo=show), `attendance_access_control`, `ticket_sales`, `optin_transactions` | Requisito externo (feedback/validacao de cobertura) | GAP |

## Figuras e Tabelas (Inventario do DOCX)

### Figuras (titulos)

- Entradas validadas (presentes) por sessao.
- Taxa de comparecimento por sessao (presentes ingressos validos).
- Ingressos (opt-in aceitos) por dia de compra.
- Curva acumulada de vendas (% do total de ingressos por sessao).
- Ingressos por segmento (proxy de relacionamento BB) - sessoes com ticket (opt-in aceitos).
- Faixa etaria (DIMAC).
- Genero (DIMAC).
- Satisfacao geral (DIMAC).
- Participacao em acoes promovidas (DIMAC).
- Percepcao: evento aproxima do BB (DIMAC).
- Leads captados por dia (CPF unicos).
- Top ativacoes (contagem de participacoes).

### Tabelas

- Publico do evento (controle de acesso - entradas validadas): Campos esperados: `Sessao`, `Ingressos validos`, `Invalidos`, `Bloqueados`, `Presentes`, `Ausentes`, `Comparecimento`.
