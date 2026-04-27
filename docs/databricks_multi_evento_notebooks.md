# Replicacao Databricks - Notebooks Multi-Evento

## Resumo

Adaptacao minima dos notebooks PySpark/SQL para processar multiplos eventos em uma unica execucao, preservando `event_id` nas Silvers e Golds. A lista hardcoded usa os 14 eventos reais com leads associados no Supabase; como `data_inicio_realizada` esta vazia, `event_date` usa `data_inicio_prevista`.

## Notebooks alterados

- `notebooks/Estudo NPBB - Segmentacao.ipynb`
- `notebooks/Survival (Ativacao e emissao).ipynb`
- `notebooks/Spend Windows & Cohorts.ipynb`
- `notebooks/Criacao de Tabelas do Estudo.ipynb`

## Pontos de alteracao identificados antes

- Filtro hardcoded por nome de evento: `event_name like ... GILBERTO GIL ...`.
- Uso de widget para evento unico.
- Uso de selecao automatica de uma unica linha para `event_id`.
- Uso de `F.max("event_date")` para uma data global.
- Criacao artificial de `event_id` por hash ou por valor fixo.
- Agregacoes por `person_key` sem `event_id`.
- `saveAsTable(... overwrite ...)` no notebook de criacao de tabelas.
- `pandas`, `plotly` e `.toPandas()` no notebook de Spend.

## Codigo removido

- Celulas 7-10 do notebook de Segmentacao deixaram de executar hardcode/widget/selecao unica.
- Notebook de Spend deixou de usar `pandas`, `plotly`, `toPandas()` e graficos locais.
- Notebook de Criacao de Tabelas deixou de usar `write.mode("overwrite").saveAsTable(...)`.

## Instrucoes de execucao no Databricks

1. Execute `Estudo NPBB - Segmentacao.ipynb` do inicio ao fim. A lista `EVENTOS_ANALISE` fica na celula 4.
2. Rode `Survival (Ativacao e emissao).ipynb` depois que `slv_timeline` estiver atualizada.
3. Rode `Spend Windows & Cohorts.ipynb` para displays PySpark/SQL filtraveis por evento.
4. Rode `Criacao de Tabelas do Estudo.ipynb` para registrar tabelas Delta por `LOCATION`, sem regravar dados.
5. Para teste com mock, no fim do notebook de Segmentacao altere `RUN_MOCK_MULTI_EVENTO = True`; a celula nao le nem escreve Delta.

## Pontos de atencao

- Matching de leads usa nome, local e data do evento; se a fonte MariaDB tiver nomes/localizacao divergentes, ajuste apenas a lista `EVENTOS_ANALISE` ou a condicao da celula 5.
- Escritas Delta continuam em `overwrite` nos paths Silver/Gold do estudo, uma vez por saida, nao dentro do loop por evento.
- Registro de tabelas usa `CREATE TABLE IF NOT EXISTS ... LOCATION`; se a tabela ja existir com location incorreta, trocar manualmente a metadata no Databricks.
- Dados BB ausentes devem ser mockados somente em celulas isoladas; o pipeline principal continua lendo tabelas corporativas.
- Para performance, monitorar joins `person_key` x eventos quando uma mesma pessoa aparecer em muitos eventos.

## Validacao realizada fora do Databricks

- JSON dos quatro notebooks validado com `json.loads`.
- Celulas Python alteradas validadas com `ast.parse`; celula SQL com `%sql` foi ignorada nessa checagem.
- Buscas sem resultado para `dbutils.widgets`, `.first()[0]`, `toPandas`, `plotly`, `import pandas`, `saveAsTable`, `monotonically_increasing_id`, `event_name like`, `TEMPO REI` e `F.max("event_date")`.
- Mock PySpark nao foi executado localmente porque o ambiente nao tem `pyspark` instalado; a celula opcional de mock foi adicionada ao fim do notebook de Segmentacao.

## Codigo novo completo por celula

### Estudo NPBB - Segmentacao.ipynb

#### Celula 4

```python
from pyspark.sql import functions as F
from pyspark.sql import types as T

base_path = "dbfs:/Volumes/transientes_pd/d5f1a1f/c1331207/EstudoNPBB"
dim_path = f"{base_path}/dim_eventos"

leads = spark.table("leads")

EVENTOS_ANALISE = [
    {"event_id": 107, "event_name": "South Summit", "event_location": "Porto Alegre / RS", "event_date": "2025-04-09"},
    {"event_id": 12, "event_name": "Gilberto Gil - SP", "event_location": "São Paulo / SP", "event_date": "2026-03-28"},
    {"event_id": 99, "event_name": "Gilberto Gil - SSA", "event_location": "Salvador / BA", "event_date": "2026-03-15"},
    {"event_id": 95, "event_name": "1ª Etapa Beach Pro Tour", "event_location": "João Pessoa / PB", "event_date": "2026-03-11"},
    {"event_id": 97, "event_name": "Copa Brasil", "event_location": "Londrina / PR", "event_date": "2026-02-27"},
    {"event_id": 106, "event_name": "1ª  Etapa Circuito Brasileiro de Vôlei de Praia -  CBVP Adulto", "event_location": "Navegantes / SC", "event_date": "2026-02-04"},
    {"event_id": 3, "event_name": "Festival de Verão", "event_location": "Salvador / BA", "event_date": "2026-01-24"},
    {"event_id": 9, "event_name": "Gilberto Gil - PA", "event_location": "Belém / PA", "event_date": "2026-03-21"},
    {"event_id": 7, "event_name": "Expodireto Cotrijal", "event_location": "Não-Me-Toque / RS", "event_date": "2026-03-09"},
    {"event_id": 5, "event_name": "Show Rural Coopavel", "event_location": "Cascavel / PR", "event_date": "2026-02-09"},
    {"event_id": 96, "event_name": "2ª Etapa Circuito Brasileiro de Vôlei de Praia", "event_location": "João Pessoa / PB", "event_date": "2026-03-04"},
    {"event_id": 11, "event_name": "Alceu Valença", "event_location": "São Paulo / SP", "event_date": "2026-03-28"},
    {"event_id": 8, "event_name": "Alceu Valença", "event_location": "Rio de Janeiro / RJ", "event_date": "2026-03-14"},
    {"event_id": 98, "event_name": "Circuito Banco do Brasil de Surf - CBBS WSL", "event_location": "Imbituba / SC", "event_date": "2026-03-25"},
]

eventos_schema = T.StructType([
    T.StructField("event_id", T.IntegerType(), False),
    T.StructField("event_name", T.StringType(), False),
    T.StructField("event_location", T.StringType(), False),
    T.StructField("event_date", T.StringType(), False),
])

eventos_analise_df = (
    spark.createDataFrame(EVENTOS_ANALISE, eventos_schema)
    .withColumn("event_date", F.to_date("event_date"))
)

dim_eventos_df = eventos_analise_df

dim_eventos_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(dim_path)
dim_eventos_df.createOrReplaceTempView("eventos_analise")

print(f"Tabela dim_eventos criada com {dim_eventos_df.count()} eventos em: {dim_path}")
display(dim_eventos_df.orderBy("event_date", "event_id"))
```

#### Celula 5

```python
from functools import reduce
from pyspark.sql import DataFrame

def _norm_text(col_name):
    return F.lower(F.trim(F.col(col_name).cast("string")))

def filtrar_leads_evento(leads_df: DataFrame, evento: dict) -> DataFrame:
    event_date_lit = F.to_date(F.lit(evento["event_date"]))

    return (
        leads_df
        .filter(
            (_norm_text("evento") == F.lit(evento["event_name"].strip().lower())) &
            (_norm_text("local") == F.lit(evento["event_location"].strip().lower())) &
            (F.to_date(F.col("data_evento")) == event_date_lit)
        )
        .filter(F.col("cpf").isNotNull())
        .withColumn("event_id", F.lit(evento["event_id"]).cast("int"))
        .withColumn("event_name", F.lit(evento["event_name"]))
        .withColumn("event_location", F.lit(evento["event_location"]))
        .withColumn("event_date", event_date_lit)
        .withColumn("evento", F.lit(evento["event_name"]))
        .withColumn("local", F.lit(evento["event_location"]))
        .withColumn("data_evento", event_date_lit)
    )
```

#### Celula 6

```python
dfs_resultado = []

for evento in EVENTOS_ANALISE:
    event_id = evento["event_id"]
    event_name = evento["event_name"]
    event_location = evento["event_location"]
    event_date = evento["event_date"]

    df_evento = filtrar_leads_evento(leads, evento)
    dfs_resultado.append(df_evento)

leads_event_df = reduce(
    lambda acc, df: acc.unionByName(df, allowMissingColumns=True),
    dfs_resultado,
)

leads_estudos = leads_event_df.filter(F.col("event_id").isNotNull())
leads_estudos.createOrReplaceTempView("leads_estudos")
leads_event_df.createOrReplaceTempView("leads_event_df")

print("Eventos no loop:", len(EVENTOS_ANALISE))
print("Leads selecionados:", leads_estudos.count())
display(
    leads_estudos
    .groupBy("event_id", "event_name", "event_location", "event_date")
    .agg(F.count("*").alias("n_leads"), F.countDistinct("cpf").alias("n_cpfs"))
    .orderBy("event_date", "event_id")
)
```

#### Celula 7

```python
# REMOVIDO: normalização hardcoded de Gilberto Gil e event_id = 1.
# A célula 6 já preserva o event_id real de EVENTOS_ANALISE.
```

#### Celula 8

```python
# REMOVIDO: alteração manual de dim_eventos_df para um único evento.
# dim_eventos_df agora vem da lista EVENTOS_ANALISE.
```

#### Celula 9

```python
# REMOVIDO: widget de sele??o para um ?nico evento.
# O processamento usa o loop em EVENTOS_ANALISE.
```

#### Celula 10

```python
# REMOVIDO: selecao automatica de um unico event_id.
# leads_estudos ja contem todos os eventos selecionados e preserva event_id.
```

#### Celula 33

```python
normalize_name_udf = F.udf(lambda s: None if s is None else " ".join([p.capitalize() for p in s.strip().split() if p]), T.StringType())

def normalize_phone(col):
    return F.regexp_replace(col, r"\D", "")

df_norm = (
    df
    .withColumn("nome_norm", normalize_name_udf(F.col("nome")))
    .withColumn("email_norm", F.lower(F.trim(F.col("email"))))
    .withColumn("telefone_norm", normalize_phone(F.col("telefone")))
    .withColumn("data_evento", F.to_date("data_evento"))
    .withColumn("event_date", F.coalesce(F.to_date("event_date"), F.col("data_evento")))
    .withColumn("data_evento", F.coalesce(F.col("data_evento"), F.col("event_date")))
    .withColumn("event_id", F.col("event_id").cast("int"))
    .withColumn("event_name", F.coalesce(F.col("event_name"), F.col("evento")))
    .withColumn("event_location", F.coalesce(F.col("event_location"), F.col("local")))
    .withColumn("data_nascimento", F.to_date("data_nascimento"))
    .withColumn("cpf_dec", to_cpf_decimal(F.col("cpf").cast("string")))
    .withColumn("cpf_hash", F.sha2(F.col("cpf_dec").cast("string"), 256))
)
```

#### Celula 35

```python
df_ev = df_norm.filter(F.col("event_id").isNotNull())
```

#### Celula 40

```python
df_keys = (
    df_dedup
    .withColumn("person_key", F.sha2(F.col("cpf_dec").cast("string"), 256))
    .withColumn("lead_id", F.sha2(F.concat_ws("|", F.col("cpf_dec").cast("string"), F.col("event_id").cast("string")), 256))
    .withColumn(
        "idade_no_evento",
        F.when(
            F.col("data_nascimento").isNotNull() & F.col("event_date").isNotNull(),
            F.floor(F.months_between(F.col("event_date"), F.col("data_nascimento")) / 12).cast("int")
        )
    )
    .withColumn(
        "faixa_etaria",
        F.when(F.col("idade_no_evento").isNull(), "sem_info")
         .when(F.col("idade_no_evento") < 18, "<18")
         .when(F.col("idade_no_evento").between(18, 24), "18-24")
         .when(F.col("idade_no_evento").between(25, 34), "25-34")
         .when(F.col("idade_no_evento").between(35, 44), "35-44")
         .when(F.col("idade_no_evento").between(45, 54), "45-54")
         .when(F.col("idade_no_evento").between(55, 64), "55-64")
         .otherwise("65+")
    )
)
```

#### Celula 42

```python
# 7.1 slv_eventos
slv_eventos_df = (
    df_keys
    .select(
        "event_id",
        "event_name",
        "event_location",
        F.col("event_date").alias("event_date")
    )
    .dropDuplicates(["event_id"])
)

# 7.2 slv_dim_pessoa
slv_dim_pessoa_df = (
    df_keys
    .select(
        "person_key",
        "cpf_hash",
        F.col("nome_norm").alias("nome"),
        F.col("email_norm").alias("email"),
        F.col("telefone_norm").alias("telefone"),
        F.year("data_nascimento").alias("birth_year"),
        F.month("data_nascimento").alias("birth_month")
    )
    .dropDuplicates(["person_key"])
)

# 7.3 slv_leads
slv_leads_df = (
    df_keys
    .select(
        "lead_id",
        "person_key",
        "event_id",
        "cpf_hash",
        F.col("event_date").alias("lead_date"),
        F.lit("evento").alias("lead_source"),
        "event_name",
        "event_location",
        "idade_no_evento",
        "faixa_etaria"
    )
    .dropDuplicates(["lead_id"])
)
```

#### Celula 99

```python
slv_cartao = spark.read.format("delta").load(f"{silver_path}/slv_cartao_base")
slv_leads_sp = spark.read.format("delta").load(f"{silver_path}/slv_leads")
df_eventos = spark.read.format("delta").load(f"{silver_path}/slv_eventos")

lead_evt_sp = (
    slv_leads_sp
    .select("person_key", "event_id")
    .dropDuplicates(["person_key", "event_id"])
    .join(df_eventos.select("event_id", "event_date"), "event_id", "left")
)

sp_core_filtered = (
    sp_core.alias("S")
    .join(lead_evt_sp.alias("E"), "person_key", "inner")
    .filter(
        (F.col("S.txn_date") >= F.date_sub(F.col("E.event_date"), 30)) &
        (F.col("S.txn_date") <= F.date_add(F.col("E.event_date"), 120))
    )
)

sp_enriched = (
    sp_core_filtered.alias("S")
    .join(
        slv_cartao
        .select("person_key", "mci", "card_id", "modalidade", "bandeira")
        .dropDuplicates()
        .alias("C"),
        on=["person_key", "mci", "card_id"],
        how="left"
    )
)

path_sp_enriched = f"{silver_path}/slv_spending_enriched"

(sp_enriched
 .write.format("delta")
 .mode("overwrite")
 .option("overwriteSchema", "true")
 .save(path_sp_enriched))

print("slv_spending_enriched salvo em:", path_sp_enriched)
print("Linhas:", sp_enriched.count())
print("Eventos:", sp_enriched.select("event_id").dropDuplicates().count())
print("Pessoas:", sp_enriched.select("person_key").dropDuplicates().count())
```

#### Celula 105

```python
lead_evt = (
    slv_leads
    .select("person_key", "event_id", "lead_date")
    .dropDuplicates(["person_key", "event_id"])
    .join(evt, "event_id", "left")
)

# =========================
# Helpers
# =========================

# 1ª transação por cartão e evento, somente transações após o evento
first_txn_by_card = (
    slv_sp_core.alias("S")
    .join(lead_evt.select("person_key", "event_id", "event_date"), "person_key")
    .filter(F.col("S.txn_date") >= F.col("event_date"))
    .groupBy("event_id", "person_key", "card_id")
    .agg(F.min("txn_date").alias("first_txn_date"))
)

# Linha do tempo, somente cartões emitidos após cada evento
# Mantém event_id para impedir mistura entre eventos da mesma pessoa.
timeline_card = (
    slv_cartao
    .select("person_key", "mci", "card_id", "plst_id", "issuance_date", "MODALIDADE", "BANDEIRA")
    .join(lead_evt.select("person_key", "event_id", "event_date", "lead_date"), "person_key")
    .filter(F.col("issuance_date") >= F.col("event_date"))
    .join(first_txn_by_card, ["event_id", "person_key", "card_id"], "left")
)
```

#### Celula 107

```python
first_issuance_by_person = (
    timeline_card
    .groupBy("event_id", "person_key")
    .agg(
        F.min("issuance_date").alias("first_issuance_date"),
        F.first("event_date").alias("event_date")
    )
)

days = spark.range(0, 121).withColumnRenamed("id", "days")

surv_emissao = (
    days.crossJoin(first_issuance_by_person)
    .withColumn(
        "is_survivor",
        (
            F.col("first_issuance_date").isNull() |
            (F.datediff(F.col("first_issuance_date"), F.col("event_date")) > F.col("days"))
        ).cast("int")
    )
    .groupBy("event_id", "days")
    .agg(
        F.sum("is_survivor").alias("n_survivors"),
        F.count("*").alias("n_at_risk")
    )
)
```

#### Celula 109

```python
base_ativacao = (
    timeline_card
    .select("event_id", "person_key", "card_id", "issuance_date", "first_txn_date")
)

days2 = spark.range(0, 121).withColumnRenamed("id", "days")

surv_ativacao = (
    days2.crossJoin(base_ativacao)
    .withColumn(
        "is_survivor",
        (
            F.col("first_txn_date").isNull() |
            (F.datediff(F.col("first_txn_date"), F.col("issuance_date")) > F.col("days"))
        ).cast("int")
    )
    .groupBy("event_id", "days")
    .agg(
        F.sum("is_survivor").alias("n_survivors"),
        F.count("*").alias("n_at_risk")
    )
)
```

#### Celula 117

```python
total_leads = (
    lead_evt
    .groupBy("event_id")
    .agg(F.countDistinct("person_key").alias("total_leads"))
)

issued_persons = (
    timeline_card
    .groupBy("event_id")
    .agg(F.countDistinct("person_key").alias("issued_persons"))
)

activation_flags = (
    timeline_card
    .withColumn("lag_issue_to_first", F.datediff("first_txn_date", "issuance_date"))
    .groupBy("event_id", "person_key")
    .agg(
        F.max(F.when(F.col("lag_issue_to_first").between(0, 30), 1).otherwise(0)).alias("activated_30"),
        F.max(F.when(F.col("lag_issue_to_first").between(0, 60), 1).otherwise(0)).alias("activated_60"),
    )
)

funil_evento = (
    total_leads
    .join(issued_persons, "event_id", "left")
    .join(
        activation_flags.groupBy("event_id").agg(
            F.sum("activated_30").alias("activated_30"),
            F.sum("activated_60").alias("activated_60"),
        ),
        "event_id",
        "left"
    )
    .fillna(0)
)

display(funil_evento.orderBy("event_id"))
```

#### Celula 119

```python
gold_path = f"{base_path}/gold"

lead_evt = (
    slv_leads
    .select("person_key", "event_id", "lead_date")
    .dropDuplicates(["person_key", "event_id"])
    .join(evt, "event_id")
)

# =========================
# 2) Enriquecimento com MCI (cliente_since_date)
# =========================

pessoa_enriched = spark.read.format("delta").load(f"{silver_path}/slv_pessoa_enriched")

pessoa_evt = (
    pessoa_enriched
    .join(lead_evt.select("event_id", "person_key", "event_date"), "person_key")
)

# =========================
# 3) Classificação correta de cliente antigo / novo por evento
# =========================

cliente_antigo = (
    pessoa_evt
    .filter(F.col("cliente_since_date") < F.col("event_date"))
    .select("event_id", "person_key")
    .dropDuplicates()
    .withColumn("cliente_antigo", F.lit(1))
)

novo_cliente = (
    pessoa_evt
    .filter(F.col("cliente_since_date") >= F.col("event_date"))
    .select("event_id", "person_key")
    .dropDuplicates()
    .withColumn("novo_cliente", F.lit(1))
)

# =========================
# 4) Regras baseadas em cartões (reemissão e upgrade)
# =========================
```

#### Celula 120

```python
cart = (
    slv_cartao
    .select("person_key", "card_id", "plst_id", "modalidade", "bandeira", "issuance_date")
    .join(lead_evt.select("event_id", "person_key", "event_date"), "person_key")
)

cart_pre = cart.filter(F.col("issuance_date") < F.col("event_date"))
cart_pos = cart.filter(F.col("issuance_date") >= F.col("event_date"))

reemissao = (
    cart_pre.select("event_id", "person_key").dropDuplicates()
    .join(cart_pos.select("event_id", "person_key").dropDuplicates(), ["event_id", "person_key"])
    .withColumn("reemissao", F.lit(1))
)

upgrade = (
    cart_pre
    .select("event_id", "person_key", "plst_id", "modalidade")
    .dropDuplicates()
    .alias("pre")
    .join(
        cart_pos.select("event_id", "person_key", "plst_id", "modalidade").dropDuplicates().alias("pos"),
        ["event_id", "person_key"]
    )
    .filter(
        (F.col("pre.plst_id") != F.col("pos.plst_id")) |
        (F.col("pre.modalidade") != F.col("pos.modalidade"))
    )
    .select("event_id", "person_key")
    .dropDuplicates()
    .withColumn("upgrade", F.lit(1))
)

classificacao = (
    lead_evt.select("event_id", "person_key", "event_date", "lead_date").dropDuplicates()
    .join(cliente_antigo, ["event_id", "person_key"], "left")
    .join(novo_cliente, ["event_id", "person_key"], "left")
    .join(reemissao, ["event_id", "person_key"], "left")
    .join(upgrade, ["event_id", "person_key"], "left")
    .fillna(0)
)

path_gold_class = f"{gold_path}/gold_cliente_classificacao"

(
    classificacao
    .write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .save(path_gold_class)
)

print("GOLD gold_cliente_classificacao salvo em:", path_gold_class)
# Databricks / PySpark
```

#### Celula 156

```python
evt = slv_eventos.select("event_id", "event_name", "event_location", "event_date").dropDuplicates()

lead_evt = (
    slv_leads.select("lead_id", "person_key", "event_id", "lead_date", "idade_no_evento", "faixa_etaria")
    .dropDuplicates(["person_key", "event_id"])
    .join(evt, "event_id", "left")
)

slv_dim_pessoa = spark.read.format("delta").load(f"{silver_path}/slv_dim_pessoa")

# ================================================
# 3) Segmento cliente pré/pós-evento (cliente_since_date)
# ================================================
p_cli = slv_pessoa_en.select("person_key", "cliente_since_date").dropDuplicates()
p_demo = slv_dim_pessoa.select("person_key", "cpf_hash", "birth_year", "birth_month").dropDuplicates()

p1 = (
    lead_evt
    .join(p_cli, "person_key", "left")
    .join(p_demo, "person_key", "left")
    .withColumn("birth_date_aprox",
        F.when(
            F.col("birth_year").isNotNull() & F.col("birth_month").isNotNull(),
            F.to_date(F.concat_ws("-", F.col("birth_year").cast("string"), F.lpad(F.col("birth_month").cast("string"), 2, "0"), F.lit("01")))
        )
    )
    .withColumn("idade_no_evento",
        F.coalesce(
            F.col("idade_no_evento"),
            F.when(F.col("birth_date_aprox").isNotNull(), F.floor(F.months_between(F.col("event_date"), F.col("birth_date_aprox")) / 12).cast("int"))
        )
    )
    .withColumn("faixa_etaria",
        F.coalesce(
            F.col("faixa_etaria"),
            F.when(F.col("idade_no_evento").isNull(), "sem_info")
             .when(F.col("idade_no_evento") < 18, "<18")
             .when(F.col("idade_no_evento").between(18, 24), "18-24")
             .when(F.col("idade_no_evento").between(25, 34), "25-34")
             .when(F.col("idade_no_evento").between(35, 44), "35-44")
             .when(F.col("idade_no_evento").between(45, 54), "45-54")
             .when(F.col("idade_no_evento").between(55, 64), "55-64")
             .otherwise("65+")
        )
    )
    .withColumn("is_cliente_pre_evento",
        F.col("cliente_since_date").isNotNull() &
        (F.col("cliente_since_date") <= F.col("event_date"))
    )
    .withColumn("is_cliente_pos_evento_d60",
        F.col("cliente_since_date").isNotNull() &
        (F.col("cliente_since_date") > F.col("event_date")) &
        (F.col("cliente_since_date") <= F.date_add(F.col("event_date"), 60))
    )
    .withColumn("seg_cliente_evento",
        F.when(F.col("is_cliente_pre_evento"), "cliente_pre")
         .when(F.col("is_cliente_pos_evento_d60"), "cliente_pos")
         .otherwise("nao_cliente")
    )
    .drop("birth_date_aprox")
)

# ================================================
# 4) Emissão + Ativação
# ================================================
per_pessoa = (
    slv_timeline
    .groupBy("event_id", "person_key")
    .agg(
        F.min("issuance_date").alias("first_issuance_date"),
        F.min("first_txn_date").alias("first_txn_date"),
        F.min("lag_event_to_issuance").alias("lag_event_to_issuance"),
        F.min("lag_issuance_to_first_txn").alias("lag_issuance_to_first_txn"),
        F.first("lag_issuance_to_first_txn_bucket", ignorenulls=True).alias("lag_issuance_to_first_txn_bucket")
    )
    .withColumn("emissao_d0_d60",
        (F.col("lag_event_to_issuance").isNotNull()) &
        (F.col("lag_event_to_issuance").between(0, 60))
    )
    .withColumn("ativacao_d30",
        (F.col("lag_issuance_to_first_txn").isNotNull()) &
        (F.col("lag_issuance_to_first_txn").between(0, 30))
    )
    .withColumn("ativacao_d60",
        (F.col("lag_issuance_to_first_txn").isNotNull()) &
        (F.col("lag_issuance_to_first_txn").between(0, 60))
    )
)

# ================================================
# 5) Spending por evento
# ================================================
sp_evt = (
    slv_sp.alias("S")
    .join(lead_evt.select("event_id", "person_key", "event_date").alias("L"), "person_key")
    .withColumn("days_since_event", F.datediff("txn_date", "event_date"))
)

agg_sp = (
    sp_evt.groupBy("event_id", "person_key")
    .agg(
        F.sum(F.when(F.col("days_since_event").between(-30, -1), F.col("amount")).otherwise(0)).alias("spend_pre_30"),
        F.sum(F.when(F.col("days_since_event").between(0, 30), F.col("amount")).otherwise(0)).alias("spend_0_30"),
        F.sum(F.when(F.col("days_since_event").between(31, 60), F.col("amount")).otherwise(0)).alias("spend_31_60"),
        F.sum(F.when(F.col("days_since_event").between(61, 90), F.col("amount")).otherwise(0)).alias("spend_61_90"),
        F.count(F.when(F.col("days_since_event").between(0, 60), True)).alias("freq_tx_0_60")
    )
    .withColumn("spend_0_60", F.col("spend_0_30") + F.col("spend_31_60"))
    .withColumn("ticket_medio_0_60",
        F.when(F.col("freq_tx_0_60") > 0, F.col("spend_0_60") / F.col("freq_tx_0_60")).otherwise(0)
    )
    .withColumn("spend_bucket_evento_0_60",
        F.when(F.col("spend_0_60") <= 0, "0")
         .when(F.col("spend_0_60") <= 100, "(0-100]")
         .when(F.col("spend_0_60") <= 500, "(100-500]")
         .when(F.col("spend_0_60") <= 2000, "(500-2000]")
         .otherwise(">2000")
    )
)

# ================================================
# 6) Bandeira/modalidade top por evento
# ================================================
w = Window.partitionBy("event_id", "person_key").orderBy(F.col("cnt").desc())

bandeira_top = (
    slv_timeline.groupBy("event_id", "person_key", "bandeira").agg(F.count("*").alias("cnt"))
    .withColumn("rn", F.row_number().over(w))
    .filter("rn=1")
    .select("event_id", "person_key", F.col("bandeira").alias("bandeira_top"))
)

modalidade_top = (
    slv_timeline.groupBy("event_id", "person_key", "modalidade").agg(F.count("*").alias("cnt"))
    .withColumn("rn", F.row_number().over(w))
    .filter("rn=1")
    .select("event_id", "person_key", F.col("modalidade").alias("modalidade_top"))
)

# ================================================
# 7) Consolidar GOLD final
# ================================================
gold_seg = (
    p1
    .join(per_pessoa, ["event_id", "person_key"], "left")
    .join(agg_sp, ["event_id", "person_key"], "left")
    .join(bandeira_top, ["event_id", "person_key"], "left")
    .join(modalidade_top, ["event_id", "person_key"], "left")
)

for col_name in ["spend_pre_30", "spend_0_30", "spend_31_60", "spend_61_90", "spend_0_60", "ticket_medio_0_60", "freq_tx_0_60"]:
    gold_seg = gold_seg.withColumn(col_name, F.coalesce(F.col(col_name), F.lit(0)))

# ================================================
# 8) Persistir GOLD
# ================================================
path_gold_seg = f"{gold_path}/gold_segmentos_pessoa"

gold_seg.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(path_gold_seg)

print("GOLD criada com sucesso:", path_gold_seg)
print("Eventos:", gold_seg.select("event_id").dropDuplicates().count())
print("Linhas pessoa-evento:", gold_seg.count())
```

#### Celula 161

```python
evt = slv_eventos.select("event_id", "event_name", "event_location", "event_date").dropDuplicates()

lead_evt = (
    slv_leads
    .select("person_key", "event_id", "lead_date")
    .dropDuplicates(["person_key", "event_id"])
    .join(evt, "event_id", "left")
)

sp_event_full = (
    slv_sp_core.alias("S")
    .join(
        lead_evt.select("person_key", "event_id", "event_date").alias("L"),
        "person_key",
        "inner"
    )
    .withColumn("days_since_event", F.datediff(F.col("S.txn_date"), F.col("L.event_date")))
)

gold_spend_event_window = (
    sp_event_full
    .groupBy("event_id", "person_key")
    .agg(
        F.sum(F.when(F.col("days_since_event").between(0, 30), F.col("amount")).otherwise(0)).cast("decimal(18,2)").alias("spend_0_30"),
        F.sum(F.when(F.col("days_since_event").between(31, 60), F.col("amount")).otherwise(0)).cast("decimal(18,2)").alias("spend_31_60"),
        F.sum(F.when(F.col("days_since_event").between(61, 90), F.col("amount")).otherwise(0)).cast("decimal(18,2)").alias("spend_61_90"),
        F.sum(F.when(F.col("days_since_event").between(-30, -1), F.col("amount")).otherwise(0)).cast("decimal(18,2)").alias("spend_pre_30")
    )
    .join(evt, "event_id", "left")
    .select("event_id", "event_name", "event_location", "event_date", "person_key", "spend_pre_30", "spend_0_30", "spend_31_60", "spend_61_90")
)

path_gold_sp_event = f"{gold_path}/gold_spend_event_window"

(
    gold_spend_event_window
    .write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .save(path_gold_sp_event)
)

print("gold_spend_event_window salvo em:", path_gold_sp_event)
print("Pessoas-evento:", gold_spend_event_window.select("event_id", "person_key").dropDuplicates().count())
```

#### Celula 168

```python
slv_timeline = spark.read.format("delta").load(f"{silver_path}/slv_timeline")

evt = slv_eventos.select("event_id", "event_name", "event_location", "event_date").dropDuplicates()
```

#### Celula 169

```python
lead_evt = (
    slv_leads
    .select("person_key", "event_id", "lead_date")
    .dropDuplicates(["person_key", "event_id"])
    .join(evt, "event_id", "left")
)
```

#### Celula 171

```python
sp_event_full = (
    slv_sp_core.alias("S")
    .join(
        lead_evt.select("person_key", "event_id", "event_date").alias("L"),
        "person_key",
        "inner"
    )
    .withColumn("days_since_event", F.datediff(F.col("S.txn_date"), F.col("L.event_date")))
)
```

#### Celula 172

```python
gold_spend_event_window = (
    sp_event_full
    .groupBy("event_id", "person_key")
    .agg(
        F.sum(
            F.when(F.col("days_since_event").between(0, 30), F.col("amount")).otherwise(0)
        ).cast("decimal(18,2)").alias("spend_0_30"),

        F.sum(
            F.when(F.col("days_since_event").between(31, 60), F.col("amount")).otherwise(0)
        ).cast("decimal(18,2)").alias("spend_31_60"),

        F.sum(
            F.when(F.col("days_since_event").between(61, 90), F.col("amount")).otherwise(0)
        ).cast("decimal(18,2)").alias("spend_61_90"),

        F.sum(
            F.when(F.col("days_since_event").between(-30, -1), F.col("amount")).otherwise(0)
        ).cast("decimal(18,2)").alias("spend_pre_30")
    )
    .join(evt, "event_id", "left")
    .select("event_id", "event_name", "event_location", "event_date", "person_key", "spend_pre_30", "spend_0_30", "spend_31_60", "spend_61_90")
)
```

#### Celula 174

```python
gold_spend_cohort = (
    slv_timeline
    .filter(F.col("issuance_date").isNotNull())
    .withColumn("cohort_week", F.date_trunc("week", F.col("issuance_date")).cast("date"))
    .groupBy("event_id", "cohort_week")
    .agg(
        F.countDistinct("card_id").alias("n_cards"),

        F.countDistinct(
            F.when(
                F.col("lag_issuance_to_first_txn").between(0, 30),
                F.col("card_id")
            )
        ).alias("cards_activated_30"),

        F.countDistinct(
            F.when(
                F.col("lag_issuance_to_first_txn").between(0, 60),
                F.col("card_id")
            )
        ).alias("cards_activated_60")
    )
    .withColumn(
        "activation_rate_30",
        F.when(F.col("n_cards") > 0, F.col("cards_activated_30") / F.col("n_cards")).otherwise(F.lit(0.0))
    )
    .withColumn(
        "activation_rate_60",
        F.when(F.col("n_cards") > 0, F.col("cards_activated_60") / F.col("n_cards")).otherwise(F.lit(0.0))
    )
    .join(evt, "event_id", "left")
    .select("event_id", "event_name", "event_location", "event_date", "cohort_week", "n_cards", "cards_activated_30", "cards_activated_60", "activation_rate_30", "activation_rate_60")
    .orderBy("event_id", "cohort_week")
)
```

#### Celula 176

```python
path_gold_sp_event = f"{gold_path}/gold_spend_event_window"
path_gold_cohort = f"{gold_path}/gold_spend_cohort"

(
    gold_spend_event_window
    .write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .save(path_gold_sp_event)
)

(
    gold_spend_cohort
    .write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .save(path_gold_cohort)
)

print("gold_spend_event_window salvo em:", path_gold_sp_event)
print("gold_spend_cohort salvo em:", path_gold_cohort)

print("Pessoas-evento com spend:", gold_spend_event_window.select("event_id", "person_key").dropDuplicates().count())
print("Cohorts evento-semana:", gold_spend_cohort.count())
```

#### Celula 181

```python
# Validação local opcional com mock: não lê nem escreve Delta.
# Troque para True quando quiser executar a validação isolada no Databricks.
RUN_MOCK_MULTI_EVENTO = False

if RUN_MOCK_MULTI_EVENTO:
    mock_eventos = spark.createDataFrame(
        [
            {"event_id": 1, "event_name": "Evento A", "event_location": "Cidade A / UF", "event_date": "2026-01-10"},
            {"event_id": 2, "event_name": "Evento B", "event_location": "Cidade B / UF", "event_date": "2026-02-10"},
        ],
        "event_id int, event_name string, event_location string, event_date string"
    ).withColumn("event_date", F.to_date("event_date"))

    mock_leads = spark.createDataFrame(
        [
            {"person_key": "p1", "lead_id": "l1", "event_id": 1, "lead_date": "2026-01-10"},
            {"person_key": "p1", "lead_id": "l2", "event_id": 2, "lead_date": "2026-02-10"},
            {"person_key": "p2", "lead_id": "l3", "event_id": 1, "lead_date": "2026-01-10"},
        ],
        "person_key string, lead_id string, event_id int, lead_date string"
    ).withColumn("lead_date", F.to_date("lead_date"))

    mock_spending = spark.createDataFrame(
        [
            {"person_key": "p1", "card_id": "c1", "txn_date": "2026-01-20", "amount": 100.0},
            {"person_key": "p1", "card_id": "c1", "txn_date": "2026-02-15", "amount": 50.0},
            {"person_key": "p1", "card_id": "c2", "txn_date": "2026-02-25", "amount": 200.0},
            {"person_key": "p2", "card_id": "c3", "txn_date": "2026-01-05", "amount": 30.0},
        ],
        "person_key string, card_id string, txn_date string, amount double"
    ).withColumn("txn_date", F.to_date("txn_date"))

    mock_lead_evt = mock_leads.join(mock_eventos, "event_id", "left")

    mock_sp_event = (
        mock_spending.alias("S")
        .join(mock_lead_evt.select("event_id", "person_key", "event_date"), "person_key")
        .withColumn("days_since_event", F.datediff("txn_date", "event_date"))
    )

    mock_gold_spend = (
        mock_sp_event.groupBy("event_id", "person_key")
        .agg(
            F.sum(F.when(F.col("days_since_event").between(-30, -1), F.col("amount")).otherwise(0)).alias("spend_pre_30"),
            F.sum(F.when(F.col("days_since_event").between(0, 30), F.col("amount")).otherwise(0)).alias("spend_0_30"),
            F.sum(F.when(F.col("days_since_event").between(31, 60), F.col("amount")).otherwise(0)).alias("spend_31_60"),
            F.sum(F.when(F.col("days_since_event").between(61, 90), F.col("amount")).otherwise(0)).alias("spend_61_90"),
        )
    )

    expected_cols = {"event_id", "person_key", "spend_pre_30", "spend_0_30", "spend_31_60", "spend_61_90"}
    assert expected_cols.issubset(set(mock_gold_spend.columns))
    assert mock_gold_spend.filter(F.col("event_id").isNull()).count() == 0
    assert mock_gold_spend.select("event_id").dropDuplicates().count() == 2

    display(mock_gold_spend.orderBy("event_id", "person_key"))
```

### Survival (Ativacao e emissao).ipynb

#### Celula 0

```python
from pyspark.sql import functions as F
from pyspark.sql.window import Window

BASE = "dbfs:/Volumes/transientes_pd/d5f1a1f/c1331207/EstudoNPBB"
SILVER = f"{BASE}/silver"
GOLD = f"{BASE}/gold"
MAX_DAYS = 120

slv_timeline = spark.read.format("delta").load(f"{SILVER}/slv_timeline").cache()
slv_eventos = spark.read.format("delta").load(f"{SILVER}/slv_eventos")

event_meta = slv_eventos.select("event_id", "event_name", "event_location", "event_date").dropDuplicates(["event_id"])
grid = spark.range(0, MAX_DAYS + 1).withColumnRenamed("id", "t")

# Survival de emissão por evento
base_e = (
    slv_timeline
    .select("event_id", "person_key", "event_date", "issuance_date")
    .dropDuplicates(["event_id", "person_key", "issuance_date"])
)

cohort_e = (
    base_e
    .filter((F.col("issuance_date").isNull()) | (F.col("issuance_date") > F.col("event_date")))
    .groupBy("event_id", "person_key", "event_date")
    .agg(F.min("issuance_date").alias("issuance_date"))
    .withColumn(
        "event_day",
        F.when(F.col("issuance_date").isNotNull(), F.datediff("issuance_date", "event_date").cast("int"))
         .otherwise(F.lit(None).cast("int"))
    )
    .cache()
)

n_cohort_e = cohort_e.groupBy("event_id").agg(F.countDistinct("person_key").alias("n_total"))

risk_e = (
    cohort_e.crossJoin(grid)
    .withColumn("at_risk", F.when(F.col("event_day").isNull(), 1).when(F.col("t") < F.col("event_day"), 1).otherwise(0))
    .withColumn("event_flag", F.when((F.col("event_day").isNotNull()) & (F.col("t") == F.col("event_day")), 1).otherwise(0))
    .groupBy("event_id", "t")
    .agg(F.sum("at_risk").alias("n_at_risk"), F.sum("event_flag").alias("d_events"))
)

km_e = (
    risk_e
    .withColumn("one_minus_h", F.when(F.col("n_at_risk") > 0, 1 - (F.col("d_events") / F.col("n_at_risk"))).otherwise(1.0))
    .withColumn("log_term", F.when(F.col("one_minus_h") > 0, F.log(F.col("one_minus_h"))).otherwise(F.lit(float("-inf"))))
)

w_e = Window.partitionBy("event_id").orderBy("t").rowsBetween(Window.unboundedPreceding, Window.currentRow)

surv_emissao = (
    km_e
    .withColumn("cum_log", F.sum("log_term").over(w_e))
    .withColumn("survival_prob", F.exp("cum_log"))
    .join(n_cohort_e, "event_id", "left")
    .join(event_meta, "event_id", "left")
    .select("event_id", "event_name", "event_location", "event_date", F.col("t").alias("days_since_event"), "survival_prob", "n_total", "n_at_risk", "d_events")
)

surv_emissao.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(f"{GOLD}/gold_survival_emissao")

print("gold_survival_emissao salvo por evento.")

# Survival de ativação por evento
base_a = (
    slv_timeline
    .select("event_id", "person_key", "event_date", "issuance_date", "first_txn_date")
    .dropDuplicates(["event_id", "person_key", "issuance_date", "first_txn_date"])
)

cohort_a = (
    base_a
    .filter(
        (F.col("issuance_date").isNotNull()) &
        (F.datediff("issuance_date", "event_date") >= 0) &
        (F.datediff("issuance_date", "event_date") <= MAX_DAYS)
    )
    .withColumn("rn", F.row_number().over(Window.partitionBy("event_id", "person_key").orderBy("issuance_date")))
    .filter("rn = 1")
    .drop("rn")
    .withColumn(
        "activation_day",
        F.when(
            (F.col("first_txn_date").isNotNull()) & (F.col("first_txn_date") >= F.col("issuance_date")),
            F.datediff("first_txn_date", "issuance_date").cast("int")
        ).otherwise(F.lit(None).cast("int"))
    )
    .cache()
)

n_cohort_a = cohort_a.groupBy("event_id").agg(F.countDistinct("person_key").alias("n_total"))

risk_a = (
    cohort_a.crossJoin(grid)
    .withColumn("at_risk", F.when(F.col("activation_day").isNull(), 1).when(F.col("t") < F.col("activation_day"), 1).otherwise(0))
    .withColumn("event_flag", F.when((F.col("activation_day").isNotNull()) & (F.col("t") == F.col("activation_day")), 1).otherwise(0))
    .groupBy("event_id", "t")
    .agg(F.sum("at_risk").alias("n_at_risk"), F.sum("event_flag").alias("d_events"))
)

km_a = (
    risk_a
    .withColumn("one_minus_h", F.when(F.col("n_at_risk") > 0, 1 - (F.col("d_events") / F.col("n_at_risk"))).otherwise(1.0))
    .withColumn("log_term", F.when(F.col("one_minus_h") > 0, F.log(F.col("one_minus_h"))).otherwise(F.lit(float("-inf"))))
)

w_a = Window.partitionBy("event_id").orderBy("t").rowsBetween(Window.unboundedPreceding, Window.currentRow)

surv_ativacao = (
    km_a
    .withColumn("cum_log", F.sum("log_term").over(w_a))
    .withColumn("survival_prob", F.exp("cum_log"))
    .join(n_cohort_a, "event_id", "left")
    .join(event_meta, "event_id", "left")
    .select("event_id", "event_name", "event_location", "event_date", F.col("t").alias("days_since_issuance"), "survival_prob", "n_total", "n_at_risk", "d_events")
)

surv_ativacao.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(f"{GOLD}/gold_survival_ativacao")

print("gold_survival_ativacao salvo por evento.")

display(surv_emissao.orderBy("event_id", "days_since_event"))
display(surv_ativacao.orderBy("event_id", "days_since_issuance"))
```

### Spend Windows & Cohorts.ipynb

#### Celula 0

```python
from pyspark.sql import functions as F

# Paths
path_root = "/Volumes/transientes_pd/d5f1a1f/c1331207/EstudoNPBB/gold"

df_spend_window = spark.read.format("delta").load(f"{path_root}/gold_spend_event_window")
df_cohort = spark.read.format("delta").load(f"{path_root}/gold_spend_cohort")

df_spend_window.createOrReplaceTempView("gold_spend_event_window")
df_cohort.createOrReplaceTempView("gold_spend_cohort")
```

#### Celula 1

```python
# Spend total por janela, filtrável por event_id/event_name no display.
spend_window_long = df_spend_window.selectExpr(
    "event_id",
    "event_name",
    "event_location",
    "event_date",
    "person_key",
    "stack(4, 'spend_pre_30', spend_pre_30, 'spend_0_30', spend_0_30, 'spend_31_60', spend_31_60, 'spend_61_90', spend_61_90) as (window, spend)"
)

display(
    spend_window_long
    .groupBy("event_id", "event_name", "event_location", "event_date", "window")
    .agg(
        F.sum("spend").alias("total_spend"),
        F.avg("spend").alias("avg_spend_por_pessoa"),
        F.countDistinct("person_key").alias("n_pessoas")
    )
    .orderBy("event_date", "event_id", "window")
)
```

#### Celula 2

```python
# Cohorts de ativação por evento e semana.
display(
    df_cohort
    .select(
        "event_id",
        "event_name",
        "event_location",
        "event_date",
        "cohort_week",
        "n_cards",
        "cards_activated_30",
        "cards_activated_60",
        "activation_rate_30",
        "activation_rate_60",
    )
    .orderBy("event_date", "event_id", "cohort_week")
)
```

#### Celula 3

```sql
%sql
SELECT
  event_id,
  event_name,
  event_location,
  event_date,
  cohort_week,
  n_cards,
  activation_rate_30,
  activation_rate_60
FROM gold_spend_cohort
ORDER BY event_date, event_id, cohort_week
```

### Criacao de Tabelas do Estudo.ipynb

#### Celula 1

```python
BASE = "/Volumes/transientes_pd/d5f1a1f/c1331207/EstudoNPBB"
CATALOG_SCHEMA = "transientes_pd.d5f1a1f"

TABELAS_DELTA = [
    ("slv_eventos", f"{BASE}/silver/slv_eventos"),
    ("slv_leads", f"{BASE}/silver/slv_leads"),
    ("slv_dim_pessoa", f"{BASE}/silver/slv_dim_pessoa"),
    ("slv_pessoa_enriched", f"{BASE}/silver/slv_pessoa_enriched"),
    ("slv_clientes_ref", f"{BASE}/silver/slv_clientes_ref"),
    ("slv_cartao_base", f"{BASE}/silver/slv_cartao_base"),
    ("slv_spending_core", f"{BASE}/silver/slv_spending_core"),
    ("slv_timeline", f"{BASE}/silver/slv_timeline"),
    ("gold_spend_event_window", f"{BASE}/gold/gold_spend_event_window"),
    ("gold_spend_cohort", f"{BASE}/gold/gold_spend_cohort"),
    ("gold_segmentos_pessoa", f"{BASE}/gold/gold_segmentos_pessoa"),
    ("gold_cliente_classificacao", f"{BASE}/gold/gold_cliente_classificacao"),
    ("gold_emissao", f"{BASE}/gold/gold_survival_emissao"),
    ("gold_ativacao", f"{BASE}/gold/gold_survival_ativacao"),
]

for table_name, location in TABELAS_DELTA:
    fqtn = f"{CATALOG_SCHEMA}.{table_name}"
    spark.sql(f"CREATE TABLE IF NOT EXISTS {fqtn} USING DELTA LOCATION '{location}'")
    print(f"Registrada se ausente: {fqtn} -> {location}")
```

#### Celula 2

```python
for table_name, _ in TABELAS_DELTA:
    fqtn = f"{CATALOG_SCHEMA}.{table_name}"
    print(f"Amostra: {fqtn}")
    display(spark.table(fqtn).limit(20))
```
