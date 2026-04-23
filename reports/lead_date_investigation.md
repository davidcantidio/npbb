# Investigação Local das Inconsistências de Data nos Leads

Artefatos gerados nesta execução:
- `scripts/investigate_lead_date_inconsistencies.py`
- `artifacts/lead_date_investigation/summary.json`
- `artifacts/lead_date_investigation/date_parsing_decision_matrix.csv`
- `artifacts/lead_date_investigation/lineage_samples.csv`

Skills aplicadas deliberadamente:
- `debugging-wizard`: estruturou a investigação em sintoma, hipótese, teste e status.
- `pandas-pro`: sustentou a inspeção quantitativa e a reconciliação de amostras.
- `python-pro`: extraiu e comparou os dois notebooks, reproduziu parsing e gerou artefatos.
- `spec-miner`: reconstruiu o contrato observado do notebook e do Gold local a partir do código.
- `ml-pipeline`: tratou a linhagem local do Gold como pipeline, não como script isolado.

## Matriz de investigação

| Sintoma | Evidência | Hipótese | Teste | Status |
|---|---|---|---|---|
| Queda forte de linhas com `data_evento` válida | `LEADS-v4.csv` tem `57.793` linhas; sob `AUTO_SAFE`, `44.394` ficam `VALID` e `13.399` ficam `AMBIGUOUS` | O notebook está rejeitando datas `MDY` ambíguas por desenho, não por invalidez objetiva | Reproduzir a matriz de parsing do notebook localmente | Confirmada |
| Execução não reproduzível entre artefatos de notebook | `.ipynb` fixa `AUTO_SAFE` e tabela UC; `.py` usa widget com default `MDY` e entrada CSV | Há drift real de configuração/implementação entre o notebook salvo e o exportado | Comparar parâmetros, fonte de dados, staging e função de parsing | Confirmada |
| Mesmo lead aparece normalizado em ISO no pipeline local | Amanda/Luis/Hannah aparecem em `LEADS-v4.csv` com barras e em `leads_multieventos_2025.csv` com ISO | O notebook provavelmente lê um estágio anterior ao output final do Gold, ou um artefato com contrato diferente | Reconciliar amostras linha a linha | Fortemente suportada, mas ainda inconclusiva sem acesso externo |
| Contrato final do Gold local parece mais rígido que o input do notebook | `validate_databricks_contract(...)` aceita o CSV final e rejeita o `raw.csv` pré-normalização | O Gold local espera publicar ISO, não strings locale-dependent | Validar `raw.csv` e `leads_multieventos_2025.csv` com o contrato | Confirmada |
| Ambiguidade também é risco no lado Gold, se o dado cru entrar como canônico | `lead_pipeline.normalization.parse_date()` usa `pd.to_datetime(..., dayfirst=True)` | Se um CSV canônico trouxer `MDY` ambíguo, o Gold pode reinterpretar silenciosamente em `DMY` | Reproduzir `parse_date("3/4/2026")`, `parse_date("3/11/2026")`, etc. | Confirmada como risco local |

## 1. Resumo executivo

O problema imediato é reproduzível localmente: `LEADS-v4.csv` contém `57.793` linhas e `data_evento` inteiramente em formato com barras. Dessas, `44.394` são `MDY` não ambíguas e `13.399` caem exatamente no conjunto ambíguo (`2/4/2026`, `2/9/2026`, `3/4/2026`, `3/9/2026`, `3/11/2026`) que o notebook com `LEAD_DATE_STYLE = "AUTO_SAFE"` marca como `AMBIGUOUS`. Isso quase reproduz o sintoma citado no brief (`57.793 -> 44.392`), com diferença residual de 2 linhas ainda não reconciliada por falta do `notebook-run(1).docx`.

O ponto mais provável de nascimento do problema não é “data inválida” no sentido estrito. É drift de contrato: o `.ipynb` salvo consome `main.main.leads_coluna_origem` com política conservadora `AUTO_SAFE`, enquanto o notebook exportado em Python já foi remodelado para entrada CSV e default `MDY`. Em paralelo, o Gold local publica saída final em ISO e passa na validação de contrato, o que indica que o notebook de enriquecimento e o Gold local não estão operando sobre o mesmo contrato de entrada.

O impacto é alto. No lado notebook, `13.399` leads deixam de ter `data_evento` utilizável para o enriquecimento. No lado Gold, há um risco distinto: se um CSV canônico com `MDY` ambíguo for processado diretamente, o parser local pode reinterpretar silenciosamente o dia e o mês em vez de rejeitar a ambiguidade.

## 2. Achados

- `Crítico | Escopo: data_evento do CSV local`
  `LEADS-v4.csv` é predominantemente `MDY` com barras; `AUTO_SAFE` transforma exatamente `13.399` linhas de `data_evento` em `AMBIGUOUS`, deixando `44.394` `VALID`.

- `Alto | Escopo: reprodutibilidade do notebook`
  O `.ipynb` e o notebook exportado `.py` não são equivalentes em contrato operacional. Eles divergem em fonte de dados, valor default de `lead_date_style` e colunas/contexto de staging.

- `Alto | Escopo: contrato de saída do Gold local`
  O output final local `leads_multieventos_2025.csv` publica `data_evento` e `data_nascimento` em ISO e passa integralmente em `validate_databricks_contract`, enquanto o `raw.csv` anterior à normalização falha nesse mesmo contrato.

- `Médio | Escopo: ingestão canônica do Gold`
  O parser `lead_pipeline.normalization.parse_date()` usa `dayfirst=True` no fallback. Se valores `MDY` ambíguos entrarem crus no caminho canônico, o resultado pode ser semanticamente errado e ainda assim “válido”.

- `Médio | Escopo: reconciliação com a execução real`
  A diferença entre `44.394` válidas reproduzidas localmente e `44.392` válidas citadas no brief permanece em aberto por falta do `.docx` e de acesso à tabela/execução reais.

## 3. Evidências

### 3.1 Perfil e matriz de parsing

Fonte: `artifacts/lead_date_investigation/date_parsing_decision_matrix.csv`

- `data_evento`
  `rows_seen=57793`
  `format_mdy_only=44394`
  `format_both_valid_different=13399`
  `auto_safe_valid_rows=44394`
  `auto_safe_ambiguous_rows=13399`

- `data_nascimento`
  `rows_seen=57793`
  `format_mdy_only=29426`
  `format_both_valid_same=1679`
  `format_both_valid_different=17661`
  `format_blank=9027`
  `auto_safe_valid_rows=29424`
  `auto_safe_ambiguous_rows=19340`
  `auto_safe_before_min_rows=1`
  `auto_safe_future_rows=1`

Exemplos concretos do conjunto ambíguo:
- `2/4/2026` -> `MDY=2026-02-04`, `DMY=2026-04-02`, `AUTO_SAFE=AMBIGUOUS`
- `3/4/2026` -> `MDY=2026-03-04`, `DMY=2026-04-03`, `AUTO_SAFE=AMBIGUOUS`
- `9/10/1999` -> `MDY=1999-09-10`, `DMY=1999-10-09`, `AUTO_SAFE=AMBIGUOUS`

### 3.2 Drift entre o `.ipynb` e o `.py`

Fontes:
- `notebook_origem1 1.ipynb`, célula 2: `LEADS_TABLE_NAME = "main.main.leads_coluna_origem"` e `LEAD_DATE_STYLE = "AUTO_SAFE"`
- `notebook_origem1 1.ipynb`, célula 4: `df_leads_raw = spark.read.table(LEADS_TABLE_NAME)`
- `notebook_origem1 1.ipynb`, célula 5: `CONTEXT_COLUMNS = ["tipo_evento", "origem"]`
- `scripts/databricks_bb_enrichment_notebook.py:57`
- `scripts/databricks_bb_enrichment_notebook.py:85`
- `scripts/databricks_bb_enrichment_notebook.py:157`
- `scripts/databricks_bb_enrichment_notebook.py:348`
- `scripts/databricks_bb_enrichment_notebook.py:511`

Diferenças confirmadas:
- Fonte de leads:
  `.ipynb` usa tabela UC.
  `.py` usa CSV (`lead_csv_path`).
- Default de estilo de data:
  `.ipynb` fixa `AUTO_SAFE`.
  `.py` defaulta `MDY`.
- Contrato de staging/contexto:
  `.ipynb` injeta `origem` e defaulta `tipo_evento/origem`.
  `.py` exige `evento`, `tipo_evento`, `local`, `data_evento`.
- Lógica de parsing:
  a função `add_date_parse_columns(...)` é a mesma no comportamento central; o drift relevante é de configuração e de entrada.

### 3.3 Contrato observado do Gold local

Fontes:
- `lead_pipeline/source_adapter.py:235`
- `lead_pipeline/source_adapter.py:276`
- `lead_pipeline/source_adapter.py:333`
- `lead_pipeline/normalization.py:161`
- `lead_pipeline/normalization.py:186`
- `lead_pipeline/contracts.py:33`
- `lead_pipeline/contracts.py:65`
- `artifacts/manual_supabase_import_2026-04-20/_pipeline_output/manual_supabase_import_2026-04-20/report.json:56`
- `artifacts/manual_supabase_import_2026-04-20/_pipeline_output/manual_supabase_import_2026-04-20/report.json:63`
- `artifacts/manual_supabase_import_2026-04-20/_pipeline_output/manual_supabase_import_2026-04-20/report.json:70`

Observações:
- O caminho canônico adapta a entrada para `ALL_COLUMNS` e a repassa para a normalização (`_adapt_canonical`).
- `parse_date(...)` aceita ISO, compactos, serial Excel e depois cai em `pd.to_datetime(..., dayfirst=True)`.
- `validate_databricks_contract(...)` exige `data_evento` em ISO no processado.
- O output final local (`47703` linhas, `34` colunas) passa sem violações de contrato.
- O `raw.csv` da mesma execução falha no contrato com:
  `CPF_INVALIDO_NO_PROCESSADO: 51838 linha(s)`
  `CPF_EVENTO_DUPLICADO_NO_PROCESSADO`
  `TELEFONE_INVALIDO_NO_PROCESSADO: 29554 linha(s)`
  `DATA_NASCIMENTO_INVALIDA_NO_PROCESSADO: 47077 linha(s)`
- O relatório local do pipeline marca `data_evento_invalid: 0`, reforçando que o Gold final não está publicando `data_evento` ambígua nesse artefato.

### 3.4 Reconciliação linha a linha

Fonte: `artifacts/lead_date_investigation/lineage_samples.csv`

1. Amanda Campos / `2ª Etapa Circuito Brasileiro de Vôlei de Praia`
   `LEADS-v4.csv:46472`
   valor local: `data_evento=3/4/2026`, `data_nascimento=5/28/1993`
   notebook: `data_evento=AMBIGUOUS`, `data_nascimento=VALID`
   Gold local sobre o valor cru: `parse_date("3/4/2026") -> 2026-04-03`
   proxy Gold local:
   `raw.csv:23354` já traz `data_evento=2026-03-04`, `data_nascimento=28/05/1993`
   `leads_multieventos_2025.csv:18576` publica `2026-03-04`, `1993-05-28`

2. Amanda Campos / `1ª Etapa Beach Pro Tour`
   `LEADS-v4.csv:52234`
   valor local: `3/11/2026`
   notebook: `AMBIGUOUS`
   Gold sobre valor cru: `2026-11-03`
   proxy Gold final: `2026-03-11`

3. Luis Gergen / `Expodireto Cotrijal`
   `LEADS-v4.csv:42307`
   valor local: `data_evento=3/9/2026`, `data_nascimento=` vazio
   notebook: `data_evento=AMBIGUOUS`, `data_nascimento=MISSING`
   Gold sobre valor cru: `2026-09-03`
   proxy Gold final:
   `raw.csv:31670` -> `2026-03-09`
   `leads_multieventos_2025.csv:26500` -> `2026-03-09`

4. Hannah Lydia Pontes Faria da Silva / `Gilberto Gil - PA`
   `LEADS-v4.csv:25446`
   valor local: `3/21/2026`, `9/24/1996`
   notebook: ambos `VALID`
   Gold sobre valor cru: `2026-03-21`, `1996-09-24`
   proxy Gold final preserva a mesma semântica:
   `raw.csv:33774`
   `leads_multieventos_2025.csv:28576`

5. Bruna Tomasi / `South Summit`
   `LEADS-v4.csv:2`
   valor local: `data_evento=3/25/2026`, `data_nascimento=9/10/1999`
   notebook: `data_evento=VALID`, `data_nascimento=AMBIGUOUS`
   Gold sobre valor cru: `data_evento=2026-03-25`, `data_nascimento=1999-10-09`
   esta amostra mostra o segundo risco: o notebook rejeita a ambiguidade; o Gold local, se recebesse o valor cru, reinterpretaria silenciosamente.

## 4. Hipóteses

- `H1. A planilha local usa predominantemente MDY, mas o notebook em AUTO_SAFE rejeita o subconjunto ambíguo por precaução.`
  Status: `Confirmada`
  A favor:
  `data_evento` tem `44.394` `mdy_only` e `13.399` `both_valid_different`; o conjunto ambíguo casa exatamente com os valores citados no brief.
  Contra:
  nenhuma evidência local relevante.

- `H2. O pipeline Gold deveria normalizar para DATE/ISO, mas está persistindo datas como string ambígua.`
  Status: `Refutada no proxy local`
  A favor:
  nenhuma no artefato final local.
  Contra:
  o final `leads_multieventos_2025.csv` passa no contrato ISO sem violações.

- `H3. O notebook não está lendo o output Gold correto; ele aponta para estágio/origem ainda não padronizado.`
  Status: `Inconclusiva, porém fortemente suportada`
  A favor:
  o `.ipynb` lê `main.main.leads_coluna_origem`; o proxy Gold local já publica ISO para os mesmos leads reconciliados.
  Contra:
  sem acesso externo à tabela real, não é possível provar a linhagem materializada.

- `H4. O Gold normaliza corretamente, mas alguma etapa posterior reserializa a data como string.`
  Status: `Refutada no proxy local`
  A favor:
  nenhuma evidência no output final local.
  Contra:
  o output final continua ISO.

- `H5. Há diferenças de configuração entre a execução real e o notebook atual.`
  Status: `Confirmada`
  A favor:
  `.ipynb` e `.py` divergem em default de `lead_date_style`, fonte de entrada e staging.
  Contra:
  sem o `.docx`, não dá para afirmar qual dos dois gerou a execução citada.

- `H6. A lógica do notebook está correta do ponto de vista defensivo, mas o contrato entre produtor e consumidor está ausente ou implícito demais.`
  Status: `Confirmada`
  A favor:
  o notebook rejeita ambiguidade explicitamente; o dado local chega com barras `MDY`; o Gold final local trabalha com ISO.
  Contra:
  nenhuma evidência local relevante.

- `H7. Existem casos reais de dados ruins além da ambiguidade de locale.`
  Status: `Confirmada`
  A favor:
  `data_nascimento` tem `9027` faltantes, `1` `BEFORE_MIN` e `1` `FUTURE`.
  Contra:
  não surgiram `UNPARSEABLE` nessa amostra local.

- `H8. O problema é misto.`
  Status: `Confirmada`
  A favor:
  o sintoma imediato está no notebook; o drift estrutural está no contrato/linhagem; há também risco local no parser do Gold.

## 5. Testes de validação executados

1. `python scripts/investigate_lead_date_inconsistencies.py`
   Resultado:
   gerou `summary.json`, `date_parsing_decision_matrix.csv` e `lineage_samples.csv`.

2. Reprodução da lógica `AUTO_SAFE` sobre `LEADS-v4.csv`
   Entrada:
   `LEADS-v4.csv`
   Esperado:
   confirmar se o conjunto ambíguo explica a queda de linhas válidas.
   Observado:
   `44.394` `VALID` + `13.399` `AMBIGUOUS` para `data_evento`.

3. Comparação de valores críticos
   Entrada:
   `2/4/2026`, `2/9/2026`, `3/4/2026`, `3/9/2026`, `3/11/2026`, `9/10/1999`
   Esperado:
   `AUTO_SAFE` rejeita o ambíguo; `MDY` resolve; `DMY` resolve para outro valor.
   Observado:
   comportamento confirmado em todos os casos.

4. Validação do contrato do Gold local
   Entrada:
   `raw.csv` e `leads_multieventos_2025.csv`
   Esperado:
   final em ISO; `raw.csv` ainda não aderente.
   Observado:
   final sem violações; `raw.csv` com múltiplas violações.

5. Reconciliação de amostras reais
   Entrada:
   Amanda, Luis, Hannah e Bruna Tomasi.
   Esperado:
   demonstrar ao menos uma cadeia causal desde valor bruto até status do notebook e proxy Gold final.
   Observado:
   Amanda e Luis mostram exatamente o padrão “notebook rejeita ambiguidade / proxy Gold final já está em ISO correto”.

## 6. Causa raiz provável

Sintoma:
- o notebook perde leads porque `data_evento` chega em string com barras e, quando ambígua, recebe status `AMBIGUOUS`.

Causa provável:
- o consumidor `.ipynb` está lendo um contrato de entrada incompatível com sua própria política `AUTO_SAFE`: strings `MDY` ambíguas, sem locale explícito.

Causa raiz mais provável:
- há drift de contrato e de artefato entre as camadas.
  Cadeia causal local mais defensável:
  `produtor/estágio cru com datas em slash MDY`
  `-> notebook salvo em UC com AUTO_SAFE`
  `-> subconjunto ambíguo vira AMBIGUOUS e não participa do enriquecimento`
  `-> a execução apresenta queda de linhas com data_evento válida`

Contribuinte estrutural adicional:
- o Gold local finaliza em ISO, mas seu parser canônico (`dayfirst=True`) também não é contrato-seguro para `MDY` ambíguo. Se a mesma matéria-prima crua chegar a ele sem normalização prévia, o erro deixa de ser rejeição e vira reinterpretacão silenciosa.

## 7. Plano de correção priorizado

- `P0 | Dados/Produtor`
  Definir contrato explícito: `data_evento` e `data_nascimento` devem sair como `YYYY-MM-DD` ou tipo nativo.
  Benefício esperado: remove ambiguidade na origem.
  Risco: baixo.
  Esforço: baixo a médio.
  Dependências: alinhamento com o produtor da tabela/arquivo.
  Validação: taxa de formatos com barra deve ir a zero no input do enriquecimento.

- `P0 | Notebook/Parsing`
  Escolher um único comportamento de consumidor:
  ou aceita apenas ISO,
  ou aceita `MDY` explicitamente quando o produtor declarar isso.
  Benefício esperado: elimina a rejeição indevida sob contrato conhecido.
  Risco: médio se for apenas trocar para `MDY` sem resolver o contrato.
  Esforço: baixo.
  Dependências: definição do contrato de entrada.
  Validação: reexecutar a matriz de parsing; o conjunto ambíguo precisa desaparecer como classe operacional.

- `P1 | Linhagem`
  Validar externamente se `main.main.leads_coluna_origem` é Gold final, staging ou tabela de origem.
  Benefício esperado: fecha H3 de forma definitiva.
  Risco: baixo.
  Esforço: baixo.
  Dependências: acesso a Databricks / `.docx`.
  Validação: schema real, query de amostra e prova de lineage.

- `P1 | Gold local`
  Endurecer `lead_pipeline.normalization.parse_date()` para não aceitar slash ambíguo por fallback `dayfirst=True`.
  Benefício esperado: evita troca silenciosa de mês/dia.
  Risco: médio, porque pode expor dados hoje mascarados.
  Esforço: médio.
  Dependências: teste de regressão por perfil de fonte.
  Validação: casos `3/4/2026`, `3/11/2026`, `9/10/1999` devem falhar ou exigir formato explícito, nunca reinterpretar.

- `P2 | Banco/Cruzamento`
  Depois do acesso externo, confirmar se o join com BB opera apenas sobre datas já normalizadas.
  Benefício esperado: fecha a assimetria entre lead e BB.
  Risco: baixo.
  Esforço: baixo.
  Dependências: acesso à tabela BB e staging real.
  Validação: schema e amostras de join.

## 8. Plano de prevenção

- Testes automatizados:
  adicionar casos fixos para `2/4/2026`, `2/9/2026`, `3/4/2026`, `3/9/2026`, `3/11/2026`, `9/10/1999`, `11/11/1974`, `12/28/1899`, `7/24/9176`.

- Contrato explícito:
  documentar para produtor e consumidor:
  tipo físico esperado,
  formato textual permitido,
  comportamento para ambiguidade,
  regra para datas fora de faixa.

- Monitoração:
  publicar métricas por coluna:
  `% ISO`,
  `% slash`,
  `% ambiguous`,
  `% before_min`,
  `% future`,
  `% missing`.

- Alertas:
  disparar quando qualquer entrada do enriquecimento contiver datas com barra sem estilo explícito, ou quando o final publicado violar `validate_databricks_contract`.

- Controle de drift:
  versionar o notebook operacional e bloquear divergência silenciosa entre `.ipynb` salvo e script exportado.

## Limitações

- `notebook-run(1).docx` não está disponível no workspace atual.
- Não houve acesso a `main.main.leads_coluna_origem` nem a `corporativos_pd.db2mci.cliente`.
- Por isso, a parte “qual artefato real alimentou a execução citada” continua pendente de evidência externa.
