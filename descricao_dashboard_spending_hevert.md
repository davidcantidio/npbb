---

name: Campos dataframe dashboards NPBB

overview: Guia em Markdown para outro agente — visuais do dashboard (PDFs), eixos, campos primários vs calculados, e mapeamento para as análises e tabelas Delta geradas pelos notebooks em notebooks/.

todos: []

isProject: false

---

# NPBB — Visuais, eixos, campos e notebooks

Este documento instrui um agente sobre **que análises os notebooks em** [notebooks/](c:\Users\NPBB\npbb\notebooks) **materializam** e como isso se relaciona com o dashboard capturado nos PDFs ([pag1.pdf](c:\Users\NPBB\Downloads\pag1.pdf), [pag2.pdf](c:\Users\NPBB\Downloads\pag2.pdf), [pag3.pdf](c:\Users\NPBB\Downloads\pag3.pdf), [Pag4.pdf](c:\Users\NPBB\Downloads\Pag4.pdf)).

**Convenção**

- **Campos primários:** vêm de fontes operacionais (leads MySQL, tabelas corporativas de cliente/cartão, fatura diária de spend, etc.) e são persistidos em camadas **Silver** com nomes estáveis `person_key`, `txn_date`, `amount`, `issuance_date`, …).
- **Campos calculados em runtime:** derivados por PySpark/SQL no pipeline — lags, flags, agregações por janela, Kaplan–Meier, taxas de coorte, buckets — habitualmente expostos em **Gold** ou em `display()` de validação.

---

## 1. Papel de cada notebook

| Notebook | Função principal | Saídas relevantes para gráficos |

|----------|------------------|----------------------------------|

| [Estudo NPBB - Segmentação.ipynb](c:\Users\NPBB\npbb\notebooks\Estudo%20NPBB%20-%20Segmentação.ipynb) | Pipeline completo: Bronze→Silver `slv_`*)→Gold `gold_`*); timeline por cartão; segmentação de cliente; janelas de spend; coortes de ativação; **testes SQL de validação** (percentis, distribuição de buckets). | `slv_timeline`, `gold_segmentos_pessoa`, `gold_spend_event_window`, `gold_spend_cohort`; consultas `.display()` sobre `slv_timeline`. |

| [Survival (Ativação e emissão).ipynb](c:\Users\NPBB\npbb\notebooks\Survival%20(Ativação%20e%20emissão).ipynb) | Estima **Kaplan–Meier** para (1) tempo até **emissão** pós-evento e (2) tempo até **ativação** (1.ª transação) pós-emissão; grava Delta e faz `display()`. | `gold/gold_survival_emissao`, `gold/gold_survival_ativacao` (registados no Unity como `gold_emissao` / `gold_ativacao` no notebook de criação de tabelas). |

| [Spend Windows & Cohorts.ipynb](c:\Users\NPBB\npbb\notebooks\Spend%20Windows%20&%20Cohorts.ipynb) | **Plotly:** barras de spend por janela (soma e média por pessoa); heatmap de taxa de ativação 30d por semana de coorte; série temporal de `activation_rate_30` e `activation_rate_60`. | Lê `gold_spend_event_window` e `gold_spend_cohort`; não grava novas Gold. |

| [Criação de Tabelas do Estudo.ipynb](c:\Users\NPBB\npbb\notebooks\Criação%20de%20Tabelas%20do%20Estudo.ipynb) | Regista tabelas Delta no catálogo e **exibe** amostras `display`). | Não cria lógica analítica nova; expõe `slv_`*, `gold_`* para SQL/Dashboards Databricks. |

---

## 2. Catálogo de visuais — dashboard (PDF) × pipeline (notebooks)

A coluna **“Onde no repo”** indica onde a lógica existe; o dashboard Databricks pode usar SQL adicional não versionado nestes `.ipynb`.

| ID | Referência no PDF | Descrição do visual / insight | Tipo de visual (inferido) | Eixo X (dimensão) | Eixo Y (métrica) | Legendas / séries | Campos primários (entrada) | Campos calculados / tabelas Gold–Silver | Onde no repo |

|----|-------------------|--------------------------------|----------------------------|-------------------|------------------|-------------------|---------------------------|----------------------------------------|--------------|

| V1 | Pág. 1 — Total de Leads | Contagem de leads únicos associados ao evento. | KPI / número único | — | Contagem | — | `lead_id` ou `person_key` nos leads; `event_id` | `COUNT(DISTINCT …)` filtrado por evento | Segmentação: `slv_leads`; agregação típica em dashboard SQL. |

| V2 | Pág. 1 — Tabela Evento, Local, Data | Metadados do evento selecionado. | Tabela | colunas: nome, local, data | — | — | `evento`, `local`, `data_evento` (leads) | `event_id`, `event_name`, `event_location`, `event_date` em `slv_eventos` | Segmentação: `slv_eventos_df` / `dim_eventos`. |

| V3 | Pág. 1 — Leads por Faixa Etária | Distribuição demográfica dos leads. | Barras ou pizza | Faixa etária (bins) | Contagem ou % de leads | — | `data_nascimento` (leads); `event_date` para idade no evento | `idade_no_evento` ou faixas; `birth_year`, `birth_month` em `slv_dim_pessoa` | Silver inclui `birth_yearbirth_month`; **faixa etária explícita** pode estar só no dashboard (derivar de `data_nascimento` + `event_date`). |

| V4 | Pág. 1 — Novos Clientes Pós-Evento vs Clientes no Evento | Compara quem já era cliente antes do evento vs quem entrou como cliente até D+60. | KPIs duplos | — | Contagem por segmento | — | `cliente_since_date` (cadastro MCI); `event_date` | `is_cliente_pre_evento`, `is_cliente_pos_evento_d60`, `seg_cliente_evento` `cliente_pre` / `cliente_pos` / `nao_cliente`) | Segmentação: bloco `gold_segmentos_pessoa` `p1` + joins). |

| V5 | Pág. 2 — Funil (Leads → Emitidos → Ativados) | Conversão em etapas, com variantes “pós-evento”. | Funil / barras empilhadas | Etapa do funil | Contagem por etapa | opcional: pós-evento vs total | `person_key`; `issuance_date`; `first_txn_date`; `event_date` | Flags por pessoa/cartão; contagens distintas; **definição “pós-evento”** alinhada ao notebook (ex.: emissão ≥ `event_date`) | Segmentação: `slv_timeline`; funil no dashboard pode espelhar agregações dessa tabela. |

| V6 | Pág. 2 — Índice de Emissão e Ativação pós Evento | Razões entre contagens do funil (ex.: emitidos/leads, ativados/emitidos). | KPIs ou gauge | — | Percentual ou índice | — | (mesmos que V5) | Divisão de contagens calculadas no SQL do painel | Dashboard SQL; dados-base em `slv_timeline` / Gold de segmentação. |

| V7 | Pág. 2 — Distribuição do Tempo até a Emissão (dias) | Histograma ou densidade dos dias entre evento e primeira emissão relevante. | Histograma | Dias desde o evento até `issuance_date` | Frequência ou densidade | — | `event_date`, `issuance_date` | `lag_event_to_issuance` (= `datediff(issuance_date, event_date)`); bins no visual | Segmentação: coluna em `slv_timeline`; validação com `APPROX_PERCENTILE(lag_event_to_issuance, …)` em SQL `.display()`. |

| V8 | Pág. 3 — Bandeira mais Emitida | Qual bandeira predomina nas emissões do universo. | Barra horizontal ou cartão KPI | `bandeira` | Volume (cartões ou pessoas) | — | `BANDEIRA` / join modalidade `slv_cartao_base`) | Ranking `count(*)` por `bandeira`; `bandeira_top` por pessoa em `gold_segmentos_pessoa` | Segmentação: agregações sobre `slv_cartao_base` / timeline. |

| V9 | Pág. 3 — Tempo de Ativação por Bucket | Agrupa o atraso entre emissão e primeira transação. | Barras | Bucket (ex.: 0–7, 8–30, …) | Contagem de cartões/pessoas | — | `issuance_date`, `first_txn_date` | `lag_issuance_to_first_txn`, `lag_issuance_to_first_txn_bucket` | Segmentação: `slv_timeline`; SQL de validação `GROUP BY lag_issuance_to_first_txn_bucket`. |

| V10 | Pág. 3 — Curvas de Sobrevivência Emissão vs Ativação | Probabilidade **acumulada** de ainda **não** ter ocorrido o evento-alvo (não emitir / não ativar) ao longo dos dias. | Duas linhas (KM) | Dias `t`) | `S(t)` probabilidade de sobrevivência | Série “Emissão” (desde evento); série “Ativação” (desde emissão) | `person_key`, `event_date`, `issuance_date`, `first_txn_date` | **Emissão:** `days_since_event`, `survival_prob`, `n_at_risk`, `d_events`; **Ativação:** `days_since_issuance`, `survival_prob`, … | **Survival.ipynb** → `gold_survival_emissao`, `gold_survival_ativacao`; Criação de Tabelas regista como `gold_emissao` / `gold_ativacao`. |

| V11 | Pág. 3 — Evolução semanal taxas 30 e 60 dias | Por **semana de emissão** `cohort_week`), mostra fração de cartões com 1.ª compra em ≤30 e ≤60 dias. | Linhas duplas ou heatmap + linhas | `cohort_week` (início da semana de `issuance_date`) | Taxa entre 0 e 1 (ou %) | Linha 30d; linha 60d | `issuance_date`, `card_id`, `lag_issuance_to_first_txn` | `n_cards`, `cards_activated_30`, `cards_activated_60`, `activation_rate_30`, `activation_rate_60` | Segmentação: `gold_spend_cohort`; **Spend Windows & Cohorts.ipynb** `go.Scatter` + heatmap). |

| V12 | Pág. 3 — Volume de Emissões × Taxa Ativação 60d | Relação entre quantidade emitida na semana e qualidade de onboarding (scatter). | Dispersão | Volume `n_cards` | `activation_rate_60` | opcional: tamanho do ponto | (derivado de `slv_timeline`) | Mesmas colunas que `gold_spend_cohort` | Pode ser reproduzido a partir de `gold_spend_cohort` no dashboard; não há scatter dedicado no Spend `.ipynb` versionado. |

| V13 | Pág. 3 — Perfil / jornada / onboarding | Mistura de produto, spend inicial, segmento cliente. | Vários cartões pequenos | Variável | Métrica | — | `modalidade`, `bandeira`, flags `emissao_d0_d60`, `ativacao_d30`, `ativacao_d60`, buckets de spend | `gold_segmentos_pessoa` (incl. `bandeira_top`, `modalidade_top`, `spend_bucket_evento_0_60`, etc.) | Segmentação: consolidação `gold_seg`. |

| V14 | Pág. 4 — Gasto por janela (0–30, 31–60, 61–90, pré-30) | Totais de spend por recorte temporal relativos ao evento; comparação por faixa etária no PDF. | Barras agrupadas / empilhadas | Janela temporal `spend_0_30`, …) | Soma ou média de spend | Séries: total, 18–40, 41+ (PDF) | `txn_date`, `amount`, `person_key`, `event_date`; demografia para filtro | `days_since_event`; colunas `spend_0_30`, `spend_31_60`, `spend_61_90`, `spend_pre_30` em `gold_spend_event_window` | Segmentação: constrói a Gold; **Spend.ipynb** barplots soma/média **sem** quebra etária no código mostrado. |

| V15 | Pág. 4 — Série semanal de gasto | Evolução semana a semana após o evento. | Linha ou área | Semana relativa ao evento | Spend agregado | Por segmento etário | `txn_date`, `amount` | `date_trunc('week', …)` + `sum(amount)` por coorte | **Não** reproduzido literalmente no Spend `.ipynb` (lá usa janelas fixas, não série semanal); dashboard pode ter SQL extra. |

---

## 3. Tabelas Delta-chave e colunas (para o agente de dados)

### 3.1 `slv_timeline` (Silver — grão típico: pessoa × cartão / linha de jornada)

| Coluna (exemplos) | Primário ou calculado | Uso típico nos gráficos |

|-------------------|----------------------|-------------------------|

| `person_key`, `card_id`, `event_id`, `event_date`, `lead_date` | Primário / chaves | Filtros, joins, eixo temporal de referência. |

| `issuance_date`, `first_txn_date` | Primário (fonte corporativa + spending) | Início de emissão e “ativação” operacional (1.ª compra). |

| `bandeira`, `modalidade` | Primário (dimensão cartão) | V8, V13. |

| `lag_event_to_issuance` | Calculado | V7, V10 (coorte emissão), funil. |

| `lag_issuance_to_first_txn`, `lag_issuance_to_first_txn_bucket` | Calculado | V9, V11. |

### 3.2 `gold_survival_emissao` / `gold_survival_ativacao`

| Coluna | Descrição | Eixo / papel no gráfico |

|--------|-----------|-------------------------|

| `days_since_event` (emissão) ou `days_since_issuance` (ativação) | Tempo discreto `t` (0…MAX_DAYS) | **Eixo X** V10. |

| `survival_prob` | Produto cumulativo dos termos KM | **Eixo Y** V10. |

| `n_at_risk`, `d_events` | Diagnóstico / transparência KM | Tooltip ou painel técnico. |

| `n_total` | Tamanho da coorte | Subtítulo ou normalização. |

### 3.3 `gold_spend_event_window`

| Coluna | Descrição |

|--------|-----------|

| `person_key` | Chave anonimizada. |

| `spend_0_30`, `spend_31_60`, `spend_61_90` | Soma de `amount` com `days_since_event` na janela indicada. |

| `spend_pre_30` | Soma com `days_since_event` entre −30 e −1. |

### 3.4 `gold_spend_cohort`

| Coluna | Descrição |

|--------|-----------|

| `cohort_week` | `date_trunc('week', issuance_date)`. |

| `n_cards` | Cartões distintos emitidos na semana. |

| `cards_activated_30`, `cards_activated_60` | Cartões com `lag_issuance_to_first_txn` em [0,30] ou [0,60]. |

| `activation_rate_30`, `activation_rate_60` | Razão ativados / `n_cards`. |

### 3.5 `gold_segmentos_pessoa`

Inclui, entre outros: `seg_cliente_evento`, flags `emissao_d0_d60`, `ativacao_d30`, `ativacao_d60`, métricas de spend agregado no pós-evento imediato `spend_0_30`, … no bloco `agg_sp`), `bandeira_top`, `modalidade_top`, `spend_bucket_evento_0_60` — alinhados a **V4, V8, V13** e parte do funil **V5**.

---

## 4. Validações numéricas (não são gráficos de produto, mas “análises” do notebook)

O notebook de segmentação executa SQL com `.display()` sobre `slv_timeline`: percentis de `lag_event_to_issuance` e `lag_issuance_to_first_txn`, distribuição de `lag_issuance_to_first_txn_bucket`, cartões por pessoa, linhas por `(person_key, card_id)`, e contagens de “emitidos sem primeira compra”. Servem para **auditoria** antes de publicar o dashboard.

---

## 5. Limitações para outro agente

1. Os PDFs são **capturas**; detalhes visuais (cores, bins exactos do histograma) podem diferir do que está nos notebooks.
2. O dashboard “NPBB - Leads Segmentados” pode conter **queries SQL** não reproduzidas fielmente neste repositório; use este MD como **mapa de dados** e confirme no workspace Databricks.
3. Quebras etárias **18–40** vs **41+** aparecem no PDF da página 4; no **Spend.ipynb** versionado só há agregação global por `window` — para replicar o PDF é preciso juntar `gold_spend_event_window` (ou `slv_spending_core`) a uma coluna de idade/faixa.

---

*Nenhuma implementação adicional foi pedida nesta iteração; este ficheiro é a especificação consolidada para orientação de agentes e humanos.*