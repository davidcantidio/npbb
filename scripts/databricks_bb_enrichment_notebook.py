# Databricks notebook source
# =============================================================================
# Notebook: Enriquecimento de Leads com Base BB
# Formato: Python notebook exportado para Databricks
# Dependencias: somente PySpark nativo + biblioteca padrao Python
# =============================================================================

# COMMAND ----------
# CELULA 1 - Imports, constantes e widgets

import re
import unicodedata

from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.window import Window


CORRUPT_RECORD_COLUMN = "_corrupt_record"
MIN_VALID_DATE = "1900-01-01"
SENTINEL_DATE = "0001-01-01"
KNOWN_INVALID_CPFS = {"12345678909"}
DATE_STYLE_OPTIONS = {"AUTO_SAFE", "DMY", "MDY"}

FINAL_OUTPUT_COLUMNS = [
    "evento",
    "data_evento",
    "Soma de ano_evento",
    "cliente",
    "cod_sexo",
    "cpf",
    "data_nascimento",
    "faixa_etaria",
    "Soma de idade",
    "local",
    "tipo_evento",
]

CONTEXT_COLUMNS = ["evento", "tipo_evento", "local", "data_evento"]

HEADER_ALIASES = {
    "dt_nascimento": "data_nascimento",
    "evento_nome": "evento",
}

NULL_TOKENS = ["", "nan", "nat", "none", "null"]

ISSUES_COLUMNS = [
    "__lead_row_id",
    "severity",
    "issue_code",
    "source",
    "field_name",
    "raw_value",
    "normalized_value",
]


dbutils.widgets.text("lead_csv_path", "")
dbutils.widgets.text("bb_table_name", "")
dbutils.widgets.text("output_final_table", "")
dbutils.widgets.text("output_audit_table", "")
dbutils.widgets.text("output_issues_table", "")
dbutils.widgets.text("csv_encoding", "UTF-8")
dbutils.widgets.text("csv_delimiter", ",")
dbutils.widgets.dropdown("lead_date_style", "AUTO_SAFE", ["AUTO_SAFE", "DMY", "MDY"])
dbutils.widgets.text("default_evento", "")
dbutils.widgets.text("default_tipo_evento", "")
dbutils.widgets.text("default_local", "")
dbutils.widgets.text("default_data_evento", "")


# COMMAND ----------
# CELULA 2 - Leitura e validacao dos parametros

def widget_text(name, default=None):
    value = dbutils.widgets.get(name)
    value = "" if value is None else str(value).strip()
    return value if value else default


def fail(message):
    raise ValueError(message)


LEAD_CSV_PATH = widget_text("lead_csv_path")
BB_TABLE_NAME = widget_text("bb_table_name")
OUTPUT_FINAL_TABLE = widget_text("output_final_table")
OUTPUT_AUDIT_TABLE = widget_text("output_audit_table")
OUTPUT_ISSUES_TABLE = widget_text("output_issues_table")
CSV_ENCODING = widget_text("csv_encoding", "UTF-8")
CSV_DELIMITER = widget_text("csv_delimiter", ",")
LEAD_DATE_STYLE = widget_text("lead_date_style", "AUTO_SAFE").upper()

DEFAULT_CONTEXT = {
    "evento": widget_text("default_evento"),
    "tipo_evento": widget_text("default_tipo_evento"),
    "local": widget_text("default_local"),
    "data_evento": widget_text("default_data_evento"),
}

if not LEAD_CSV_PATH:
    fail("Parametro obrigatorio ausente: lead_csv_path")
if not BB_TABLE_NAME:
    fail("Parametro obrigatorio ausente: bb_table_name")
if CSV_DELIMITER is None or len(CSV_DELIMITER) != 1:
    fail("csv_delimiter deve conter exatamente um caractere")
if LEAD_DATE_STYLE not in DATE_STYLE_OPTIONS:
    fail(f"lead_date_style invalido: {LEAD_DATE_STYLE}. Use AUTO_SAFE, DMY ou MDY")


# COMMAND ----------
# CELULA 3 - Funcoes auxiliares puras

def strip_accents(value):
    normalized = unicodedata.normalize("NFKD", str(value or ""))
    return "".join(char for char in normalized if not unicodedata.combining(char))


def normalize_header(header):
    value = strip_accents(str(header or "").lstrip("\ufeff").strip().lower())
    value = re.sub(r"[^a-z0-9]+", "_", value).strip("_")
    return HEADER_ALIASES.get(value, value)


def safe_col(column_name):
    escaped = str(column_name).replace("`", "``")
    return F.col(f"`{escaped}`")


def calc_cpf_check_digit(numbers, start_weight):
    total = 0
    weight = start_weight
    for number in numbers:
        total += number * weight
        weight -= 1
    remainder = total % 11
    return 0 if remainder < 2 else 11 - remainder


def is_valid_cpf(value):
    digits = re.sub(r"\D+", "", str(value or ""))
    if len(digits) != 11:
        return False
    if digits == digits[0] * 11:
        return False
    if digits in KNOWN_INVALID_CPFS:
        return False
    numbers = [int(character) for character in digits]
    first = calc_cpf_check_digit(numbers[:9], 10)
    second = calc_cpf_check_digit(numbers[:10], 11)
    return first == numbers[9] and second == numbers[10]


validate_cpf_udf = F.udf(is_valid_cpf, T.BooleanType())


def try_timestamp(column_name, pattern):
    escaped = str(column_name).replace("`", "``")
    pattern_escaped = str(pattern).replace("'", "\\'")
    return F.expr(f"try_to_timestamp(`{escaped}`, '{pattern_escaped}')")


def empty_issues_df():
    schema = T.StructType(
        [
            T.StructField("__lead_row_id", T.StringType(), True),
            T.StructField("severity", T.StringType(), False),
            T.StructField("issue_code", T.StringType(), False),
            T.StructField("source", T.StringType(), False),
            T.StructField("field_name", T.StringType(), True),
            T.StructField("raw_value", T.StringType(), True),
            T.StructField("normalized_value", T.StringType(), True),
        ]
    )
    return spark.createDataFrame([], schema=schema)


# COMMAND ----------
# CELULA 4 - Leitura do CSV de leads e controle de linhas corrompidas

csv_reader_options = {
    "header": "true",
    "inferSchema": "false",
    "mode": "PERMISSIVE",
    "encoding": CSV_ENCODING,
    "sep": CSV_DELIMITER,
}

header_probe_df = spark.read.options(**csv_reader_options).csv(LEAD_CSV_PATH)

if not header_probe_df.columns:
    fail("CSV de leads sem cabecalho ou sem colunas detectaveis.")

if CORRUPT_RECORD_COLUMN in header_probe_df.columns:
    fail(f"CSV contem coluna reservada pelo notebook: {CORRUPT_RECORD_COLUMN}")

lead_csv_schema = T.StructType(
    [T.StructField(column, T.StringType(), True) for column in header_probe_df.columns]
    + [T.StructField(CORRUPT_RECORD_COLUMN, T.StringType(), True)]
)

raw_leads_df = (
    spark.read.options(**csv_reader_options)
    .option("columnNameOfCorruptRecord", CORRUPT_RECORD_COLUMN)
    .schema(lead_csv_schema)
    .csv(LEAD_CSV_PATH)
)

corrupt_rows_df = raw_leads_df.filter(F.col(CORRUPT_RECORD_COLUMN).isNotNull())
corrupt_rows_count = corrupt_rows_df.count()
corrupt_rows_df.createOrReplaceTempView("corrupt_rows_df")

if corrupt_rows_count > 0:
    display(corrupt_rows_df)
    fail(f"CSV contem {corrupt_rows_count} linha(s) corrompida(s). Corrija antes do enriquecimento.")


# COMMAND ----------
# CELULA 5 - Normalizacao de cabecalhos, contrato minimo e staging rastreavel

source_columns = [column for column in raw_leads_df.columns if column != CORRUPT_RECORD_COLUMN]
normalized_columns = [normalize_header(column) for column in source_columns]

duplicates = sorted(
    {
        column
        for column in normalized_columns
        if normalized_columns.count(column) > 1
    }
)
if duplicates:
    fail(f"Cabecalhos duplicados apos normalizacao: {', '.join(duplicates)}")

raw_payload = F.to_json(F.struct(*[safe_col(column).alias(column) for column in source_columns]))

staging_leads_df = raw_leads_df.select(
    *[
        safe_col(source).alias(target)
        for source, target in zip(source_columns, normalized_columns)
    ],
    raw_payload.alias("__lead_raw_payload_json"),
    F.input_file_name().alias("__input_file_name"),
)

if "cpf" not in staging_leads_df.columns:
    fail("Coluna obrigatoria ausente apos normalizacao: cpf")

missing_context = []
for column in CONTEXT_COLUMNS:
    if column not in staging_leads_df.columns and not DEFAULT_CONTEXT.get(column):
        missing_context.append(column)
    if column not in staging_leads_df.columns and DEFAULT_CONTEXT.get(column):
        staging_leads_df = staging_leads_df.withColumn(column, F.lit(DEFAULT_CONTEXT[column]).cast("string"))

if missing_context:
    fail("Contexto obrigatorio ausente e sem default: " + ", ".join(missing_context))

if "data_nascimento" not in staging_leads_df.columns:
    staging_leads_df = staging_leads_df.withColumn("data_nascimento", F.lit(None).cast("string"))

staging_leads_df = (
    staging_leads_df.withColumn("__row_uid", F.monotonically_increasing_id())
    .withColumn(
        "__lead_row_id",
        F.sha2(
            F.concat_ws(
                "||",
                F.coalesce(F.col("__input_file_name"), F.lit("")),
                F.col("__row_uid").cast("string"),
            ),
            256,
        ),
    )
    .drop("__row_uid")
    .withColumn("__cpf_raw", F.col("cpf").cast("string"))
    .withColumn("__data_evento_raw", F.col("data_evento").cast("string"))
    .withColumn("__data_nascimento_raw", F.col("data_nascimento").cast("string"))
)

for column in ["evento", "tipo_evento", "local", "data_evento", "data_nascimento"]:
    staging_leads_df = staging_leads_df.withColumn(column, F.col(column).cast("string"))

input_leads_count = staging_leads_df.count()
staging_leads_df.createOrReplaceTempView("staging_leads_df_raw")


# COMMAND ----------
# CELULA 6 - Padronizacao e validacao de CPF nos leads

cpf_digits = F.regexp_replace(F.coalesce(F.col("__cpf_raw"), F.lit("")), r"[^0-9]", "")
cpf_digits_len = F.length(cpf_digits)
cpf_normalized = F.when(cpf_digits_len.between(1, 11), F.lpad(cpf_digits, 11, "0"))
cpf_repeated = cpf_normalized.rlike(r"^(\d)\1{10}$")

cpf_issue_code = (
    F.when(cpf_digits_len == 0, F.lit("CPF_EMPTY"))
    .when(cpf_digits_len > 11, F.lit("CPF_GT_11"))
    .when(cpf_repeated, F.lit("CPF_REPEATED_DIGITS"))
    .when(cpf_normalized == F.lit("12345678909"), F.lit("CPF_KNOWN_PLACEHOLDER"))
    .when(~validate_cpf_udf(cpf_normalized), F.lit("CPF_CHECK_DIGIT_INVALID"))
)

staging_leads_df = (
    staging_leads_df.withColumn("cpf_digits_raw", cpf_digits)
    .withColumn("cpf_digits_len", cpf_digits_len)
    .withColumn("cpf_normalizado_11", cpf_normalized)
    .withColumn("cpf_lpad_applied", cpf_digits_len.between(1, 10))
    .withColumn("cpf_issue_code", cpf_issue_code)
    .withColumn("cpf_valido", F.col("cpf_issue_code").isNull())
    .withColumn(
        "cpf_output",
        F.when(cpf_digits_len.between(1, 11), F.col("cpf_normalizado_11")).otherwise(F.lit(None).cast("string")),
    )
)


# COMMAND ----------
# CELULA 7 - Parsing seguro de datas dos leads

def clean_text_column(column_name):
    cleaned = F.trim(F.col(column_name))
    return F.when(F.lower(cleaned).isin(*NULL_TOKENS), F.lit(None).cast("string")).otherwise(cleaned)


def add_date_parse_columns(df, raw_column, prefix, date_kind):
    clean_col = f"{prefix}_clean"
    candidate_col = f"{prefix}_candidate"
    status_col = f"{prefix}_status"
    valid_col = f"{prefix}_valid"

    df = df.withColumn(clean_col, clean_text_column(raw_column))

    iso_candidate = F.to_date(
        F.coalesce(
            try_timestamp(clean_col, "yyyy-MM-dd HH:mm:ss.SSSSSS"),
            try_timestamp(clean_col, "yyyy-MM-dd HH:mm:ss.SSS"),
            try_timestamp(clean_col, "yyyy-MM-dd HH:mm:ss"),
            try_timestamp(clean_col, "yyyy-MM-dd"),
        )
    )

    slash_like = F.col(clean_col).rlike(r"^\d{1,2}/\d{1,2}/\d{4}(?: \d{1,2}:\d{1,2}(?::\d{1,2})?)?$")
    first_token = F.regexp_extract(F.col(clean_col), r"^(\d{1,2})/", 1).cast("int")
    second_token = F.regexp_extract(F.col(clean_col), r"^\d{1,2}/(\d{1,2})/", 1).cast("int")
    ambiguous_slash = slash_like & first_token.between(1, 12) & second_token.between(1, 12)

    dmy_candidate = F.to_date(
        F.coalesce(
            try_timestamp(clean_col, "d/M/yyyy H:m:s"),
            try_timestamp(clean_col, "d/M/yyyy H:m"),
            try_timestamp(clean_col, "d/M/yyyy"),
        )
    )
    mdy_candidate = F.to_date(
        F.coalesce(
            try_timestamp(clean_col, "M/d/yyyy H:m:s"),
            try_timestamp(clean_col, "M/d/yyyy H:m"),
            try_timestamp(clean_col, "M/d/yyyy"),
        )
    )

    if LEAD_DATE_STYLE == "DMY":
        slash_candidate = F.when(slash_like, dmy_candidate)
        is_ambiguous = F.lit(False)
    elif LEAD_DATE_STYLE == "MDY":
        slash_candidate = F.when(slash_like, mdy_candidate)
        is_ambiguous = F.lit(False)
    else:
        slash_candidate = (
            F.when(slash_like & (first_token > 12), dmy_candidate)
            .when(slash_like & (second_token > 12), mdy_candidate)
        )
        is_ambiguous = ambiguous_slash

    candidate = F.coalesce(iso_candidate, slash_candidate)
    min_date = F.to_date(F.lit(MIN_VALID_DATE))

    if date_kind == "birth":
        status = (
            F.when(F.col(clean_col).isNull(), F.lit("MISSING"))
            .when(is_ambiguous, F.lit("AMBIGUOUS"))
            .when(candidate.isNull(), F.lit("UNPARSEABLE"))
            .when(candidate < min_date, F.lit("BEFORE_MIN"))
            .when(candidate > F.current_date(), F.lit("FUTURE"))
            .otherwise(F.lit("VALID"))
        )
    else:
        status = (
            F.when(F.col(clean_col).isNull(), F.lit("MISSING"))
            .when(is_ambiguous, F.lit("AMBIGUOUS"))
            .when(candidate.isNull(), F.lit("UNPARSEABLE"))
            .when(candidate < min_date, F.lit("BEFORE_MIN"))
            .otherwise(F.lit("VALID"))
        )

    return (
        df.withColumn(candidate_col, candidate)
        .withColumn(status_col, status)
        .withColumn(valid_col, F.when(F.col(status_col) == F.lit("VALID"), F.col(candidate_col)))
    )


staging_leads_df = add_date_parse_columns(
    staging_leads_df,
    "__data_nascimento_raw",
    "lead_birthdate",
    "birth",
)
staging_leads_df = add_date_parse_columns(
    staging_leads_df,
    "__data_evento_raw",
    "lead_event_date",
    "event",
)

valid_event_rows = staging_leads_df.filter(F.col("lead_event_date_status") == F.lit("VALID")).count()
if valid_event_rows == 0:
    fail("Nenhuma linha possui data_evento valida. Notebook abortado.")

staging_leads_df = staging_leads_df.cache()
staging_leads_df.createOrReplaceTempView("staging_leads_df")


# COMMAND ----------
# CELULA 8 - Shortlist de CPFs elegiveis para match

lead_cpfs_matchable = (
    staging_leads_df.filter(F.col("cpf_valido"))
    .select(F.col("cpf_normalizado_11").alias("cpf_match"))
    .distinct()
)

lead_cpfs_matchable.createOrReplaceTempView("lead_cpfs_matchable")


# COMMAND ----------
# CELULA 9 - Leitura enxuta, filtro tecnico e deduplicacao da base BB

bb_required_columns = {"cod_tipo", "cod_cpf_cgc", "dta_nasc_csnt", "dta_ulta_atlz", "dta_revisao", "cod"}
bb_available_columns = set(spark.table(BB_TABLE_NAME).columns)
bb_missing_columns = sorted(bb_required_columns - bb_available_columns)
if bb_missing_columns:
    fail("Base BB sem colunas obrigatorias: " + ", ".join(bb_missing_columns))

bb_base_df = (
    spark.table(BB_TABLE_NAME)
    .select("cod_tipo", "cod_cpf_cgc", "dta_nasc_csnt", "dta_ulta_atlz", "dta_revisao", "cod")
    .where(F.col("cod_tipo") == F.lit(1))
    .where(F.col("cod_cpf_cgc").isNotNull())
    .withColumn("bb_cpf_text", F.col("cod_cpf_cgc").cast("string"))
    .withColumn("bb_cpf_digits", F.regexp_replace(F.col("bb_cpf_text"), r"[^0-9]", ""))
    .withColumn("bb_cpf_len", F.length(F.col("bb_cpf_digits")))
    .where(F.col("bb_cpf_len").between(1, 11))
    .withColumn("bb_cpf_normalizado_11", F.lpad(F.col("bb_cpf_digits"), 11, "0"))
)

bb_pruned_df = (
    bb_base_df.join(
        F.broadcast(lead_cpfs_matchable),
        bb_base_df["bb_cpf_normalizado_11"] == lead_cpfs_matchable["cpf_match"],
        "left_semi",
    )
    .withColumn("bb_cpf_valido", validate_cpf_udf(F.col("bb_cpf_normalizado_11")))
    .where(F.col("bb_cpf_valido"))
)

sentinel_date = F.to_date(F.lit(SENTINEL_DATE))
min_date = F.to_date(F.lit(MIN_VALID_DATE))

bb_pruned_df = (
    bb_pruned_df.withColumn(
        "bb_dta_ulta_atlz_ord",
        F.when(F.col("dta_ulta_atlz") == sentinel_date, F.lit(None).cast("date")).otherwise(F.col("dta_ulta_atlz")),
    )
    .withColumn(
        "bb_dta_revisao_ord",
        F.when(F.col("dta_revisao") == sentinel_date, F.lit(None).cast("date")).otherwise(F.col("dta_revisao")),
    )
    .withColumn(
        "bb_dta_nasc_valid",
        F.when(F.col("dta_nasc_csnt") == sentinel_date, F.lit(None).cast("date"))
        .when(F.col("dta_nasc_csnt") < min_date, F.lit(None).cast("date"))
        .when(F.col("dta_nasc_csnt") > F.current_date(), F.lit(None).cast("date"))
        .otherwise(F.col("dta_nasc_csnt")),
    )
    .withColumn(
        "bb_tiebreak_hash",
        F.sha2(
            F.to_json(F.struct("bb_cpf_normalizado_11", "dta_ulta_atlz", "dta_revisao", "cod")),
            256,
        ),
    )
    .cache()
)

bb_rows_after_prune = bb_pruned_df.count()

bb_window = Window.partitionBy("bb_cpf_normalizado_11").orderBy(
    F.col("bb_dta_ulta_atlz_ord").desc_nulls_last(),
    F.col("bb_dta_revisao_ord").desc_nulls_last(),
    F.col("cod").desc_nulls_last(),
    F.col("bb_tiebreak_hash").desc(),
)

bb_dedup_df = (
    bb_pruned_df.withColumn("bb_row_num", F.row_number().over(bb_window))
    .where(F.col("bb_row_num") == F.lit(1))
    .drop("bb_row_num")
    .cache()
)

bb_rows_after_dedupe = bb_dedup_df.count()
bb_max_dta_ulta_atlz = bb_dedup_df.agg(F.max("bb_dta_ulta_atlz_ord").alias("max_date")).collect()[0]["max_date"]
bb_max_dta_ulta_atlz = str(bb_max_dta_ulta_atlz) if bb_max_dta_ulta_atlz is not None else None

bb_dedup_df.createOrReplaceTempView("bb_dedup_df")


# COMMAND ----------
# CELULA 10 - Join leads <- BB e reconciliacao dos campos

joined_df = staging_leads_df.join(
    bb_dedup_df,
    (staging_leads_df["cpf_valido"])
    & (staging_leads_df["cpf_normalizado_11"] == bb_dedup_df["bb_cpf_normalizado_11"]),
    "left",
)

joined_df = (
    joined_df.withColumn("cliente", F.col("bb_cpf_normalizado_11").isNotNull())
    .withColumn(
        "match_status",
        F.when(~F.col("cpf_valido"), F.lit("INVALID_CPF"))
        .when(F.col("bb_cpf_normalizado_11").isNotNull(), F.lit("MATCHED"))
        .otherwise(F.lit("NO_MATCH")),
    )
    .withColumn("data_nascimento_final", F.coalesce(F.col("bb_dta_nasc_valid"), F.col("lead_birthdate_valid")))
    .withColumn(
        "birthdate_source",
        F.when(F.col("bb_dta_nasc_valid").isNotNull(), F.lit("bb"))
        .when(F.col("lead_birthdate_valid").isNotNull(), F.lit("lead"))
        .otherwise(F.lit("none")),
    )
    .withColumn("data_evento_final", F.col("lead_event_date_valid"))
    .withColumn("cod_sexo_final", F.lit(None).cast("string"))
    .withColumn(
        "required_context_missing",
        (F.length(F.trim(F.coalesce(F.col("evento"), F.lit("")))) == 0)
        | (F.length(F.trim(F.coalesce(F.col("tipo_evento"), F.lit("")))) == 0)
        | (F.length(F.trim(F.coalesce(F.col("local"), F.lit("")))) == 0),
    )
)

joined_count = joined_df.count()
unique_row_ids = joined_df.select("__lead_row_id").distinct().count()
if joined_count != input_leads_count:
    fail(f"Join alterou cardinalidade: entrada={input_leads_count}, saida={joined_count}")
if unique_row_ids != input_leads_count:
    fail(f"__lead_row_id perdeu unicidade: entrada={input_leads_count}, unicos={unique_row_ids}")

joined_df = joined_df.cache()
joined_df.createOrReplaceTempView("joined_df")


# COMMAND ----------
# CELULA 11 - Derivacoes de negocio e montagem do final_df

joined_df = (
    joined_df.withColumn("Soma de ano_evento", F.year(F.col("data_evento_final")).cast("int"))
    .withColumn(
        "Soma de idade",
        F.when(
            F.col("data_evento_final").isNotNull() & F.col("data_nascimento_final").isNotNull(),
            (F.year(F.col("data_evento_final")) - F.year(F.col("data_nascimento_final"))).cast("int"),
        ).otherwise(F.lit(None).cast("int")),
    )
    .withColumn(
        "faixa_etaria",
        F.when(F.col("Soma de idade").isNull(), F.lit("Desconhecido"))
        .when(F.col("Soma de idade") < 18, F.lit("<18"))
        .when(F.col("Soma de idade") <= 40, F.lit("18-40"))
        .otherwise(F.lit("40+")),
    )
)

final_df = joined_df.select(
    F.col("evento").alias("evento"),
    F.col("data_evento_final").alias("data_evento"),
    F.col("Soma de ano_evento"),
    F.col("cliente"),
    F.col("cod_sexo_final").alias("cod_sexo"),
    F.col("cpf_output").alias("cpf"),
    F.col("data_nascimento_final").alias("data_nascimento"),
    F.col("faixa_etaria"),
    F.col("Soma de idade"),
    F.col("local"),
    F.col("tipo_evento"),
)

if final_df.columns != FINAL_OUTPUT_COLUMNS:
    fail("Layout final invalido: " + str(final_df.columns))

if final_df.count() != input_leads_count:
    fail("final_df nao preservou a cardinalidade dos leads")

final_df.createOrReplaceTempView("final_df")


# COMMAND ----------
# CELULA 12 - Montagem do issues_df por linha

issues_df = empty_issues_df()

cpf_issues_df = joined_df.filter(F.col("cpf_issue_code").isNotNull()).select(
    F.col("__lead_row_id"),
    F.lit("error").alias("severity"),
    F.col("cpf_issue_code").alias("issue_code"),
    F.lit("leads").alias("source"),
    F.lit("cpf").alias("field_name"),
    F.col("__cpf_raw").cast("string").alias("raw_value"),
    F.col("cpf_output").cast("string").alias("normalized_value"),
)

birth_ambiguous_df = joined_df.filter(F.col("lead_birthdate_status") == F.lit("AMBIGUOUS")).select(
    F.col("__lead_row_id"),
    F.lit("error").alias("severity"),
    F.lit("DATE_AMBIGUOUS").alias("issue_code"),
    F.lit("leads").alias("source"),
    F.lit("data_nascimento").alias("field_name"),
    F.col("__data_nascimento_raw").cast("string").alias("raw_value"),
    F.lit(None).cast("string").alias("normalized_value"),
)

birth_invalid_df = joined_df.filter(
    F.col("lead_birthdate_status").isin("UNPARSEABLE", "BEFORE_MIN", "FUTURE")
).select(
    F.col("__lead_row_id"),
    F.lit("error").alias("severity"),
    F.lit("LEAD_BIRTHDATE_INVALID").alias("issue_code"),
    F.lit("leads").alias("source"),
    F.lit("data_nascimento").alias("field_name"),
    F.col("__data_nascimento_raw").cast("string").alias("raw_value"),
    F.col("lead_birthdate_candidate").cast("string").alias("normalized_value"),
)

event_ambiguous_df = joined_df.filter(F.col("lead_event_date_status") == F.lit("AMBIGUOUS")).select(
    F.col("__lead_row_id"),
    F.lit("error").alias("severity"),
    F.lit("DATE_AMBIGUOUS").alias("issue_code"),
    F.lit("leads").alias("source"),
    F.lit("data_evento").alias("field_name"),
    F.col("__data_evento_raw").cast("string").alias("raw_value"),
    F.lit(None).cast("string").alias("normalized_value"),
)

event_invalid_df = joined_df.filter(
    F.col("lead_event_date_status").isin("MISSING", "UNPARSEABLE", "BEFORE_MIN")
).select(
    F.col("__lead_row_id"),
    F.lit("error").alias("severity"),
    F.lit("LEAD_EVENT_DATE_INVALID").alias("issue_code"),
    F.lit("leads").alias("source"),
    F.lit("data_evento").alias("field_name"),
    F.col("__data_evento_raw").cast("string").alias("raw_value"),
    F.col("lead_event_date_candidate").cast("string").alias("normalized_value"),
)

context_missing_df = joined_df.filter(F.col("required_context_missing")).select(
    F.col("__lead_row_id"),
    F.lit("error").alias("severity"),
    F.lit("MISSING_REQUIRED_CONTEXT").alias("issue_code"),
    F.lit("leads").alias("source"),
    F.lit("evento|tipo_evento|local").alias("field_name"),
    F.concat_ws(
        " | ",
        F.coalesce(F.col("evento"), F.lit("")),
        F.coalesce(F.col("tipo_evento"), F.lit("")),
        F.coalesce(F.col("local"), F.lit("")),
    ).alias("raw_value"),
    F.lit(None).cast("string").alias("normalized_value"),
)

for frame in [
    cpf_issues_df,
    birth_ambiguous_df,
    birth_invalid_df,
    event_ambiguous_df,
    event_invalid_df,
    context_missing_df,
]:
    issues_df = issues_df.unionByName(frame.select(*ISSUES_COLUMNS), allowMissingColumns=False)

issues_df.createOrReplaceTempView("issues_df")


# COMMAND ----------
# CELULA 13 - Montagem do audit_df em formato longo

AUDIT_DIMENSION_COLUMNS = ["evento", "tipo_evento"]


def metric_long_df(df, scope, metric_exprs, group_columns=None):
    group_columns = group_columns or []
    metric_names = [name for name, _expr in metric_exprs]

    if group_columns:
        wide_df = df.groupBy(*group_columns).agg(*[expr.alias(name) for name, expr in metric_exprs])
    else:
        wide_df = df.agg(*[expr.alias(name) for name, expr in metric_exprs])

    wide_df = wide_df.withColumn("escopo", F.lit(scope))
    for column in AUDIT_DIMENSION_COLUMNS:
        if column not in group_columns:
            wide_df = wide_df.withColumn(column, F.lit(None).cast("string"))

    metric_array = F.array(
        *[
            F.struct(F.lit(name).alias("metrica"), F.col(name).cast("string").alias("valor"))
            for name in metric_names
        ]
    )
    return (
        wide_df.select("escopo", "evento", "tipo_evento", F.explode(metric_array).alias("metric"))
        .select(
            "escopo",
            "evento",
            "tipo_evento",
            F.col("metric.metrica").alias("metrica"),
            F.col("metric.valor").alias("valor"),
        )
    )


base_metrics = [
    ("total_rows", F.count(F.lit(1))),
    ("cpf_valid_rows", F.sum(F.when(F.col("cpf_valido"), F.lit(1)).otherwise(F.lit(0)))),
    ("cpf_invalid_rows", F.sum(F.when(~F.col("cpf_valido"), F.lit(1)).otherwise(F.lit(0)))),
    ("cpf_valid_unique", F.countDistinct(F.when(F.col("cpf_valido"), F.col("cpf_output")))),
    ("bb_match_rows", F.sum(F.when(F.col("cliente"), F.lit(1)).otherwise(F.lit(0)))),
    ("bb_match_unique", F.countDistinct(F.when(F.col("cliente"), F.col("cpf_output")))),
    ("bb_no_match_rows", F.sum(F.when(F.col("match_status") == F.lit("NO_MATCH"), F.lit(1)).otherwise(F.lit(0)))),
    ("bb_no_match_unique", F.countDistinct(F.when(F.col("match_status") == F.lit("NO_MATCH"), F.col("cpf_output")))),
    ("lead_birthdate_missing_rows", F.sum(F.when(F.col("lead_birthdate_status") == F.lit("MISSING"), F.lit(1)).otherwise(F.lit(0)))),
    (
        "lead_birthdate_invalid_rows",
        F.sum(
            F.when(
                F.col("lead_birthdate_status").isin("AMBIGUOUS", "UNPARSEABLE", "BEFORE_MIN", "FUTURE"),
                F.lit(1),
            ).otherwise(F.lit(0))
        ),
    ),
    ("lead_event_date_invalid_rows", F.sum(F.when(F.col("lead_event_date_status") != F.lit("VALID"), F.lit(1)).otherwise(F.lit(0)))),
    ("birthdate_filled_from_bb_rows", F.sum(F.when(F.col("birthdate_source") == F.lit("bb"), F.lit(1)).otherwise(F.lit(0)))),
    ("final_birthdate_null_rows", F.sum(F.when(F.col("data_nascimento_final").isNull(), F.lit(1)).otherwise(F.lit(0)))),
    ("cpf_lpad_applied_rows", F.sum(F.when(F.col("cpf_lpad_applied"), F.lit(1)).otherwise(F.lit(0)))),
]

global_metrics = base_metrics + [
    ("corrupt_rows", F.lit(corrupt_rows_count)),
    ("bb_rows_after_prune", F.lit(bb_rows_after_prune)),
    ("bb_rows_after_dedupe", F.lit(bb_rows_after_dedupe)),
    ("bb_max_dta_ulta_atlz", F.lit(bb_max_dta_ulta_atlz)),
]

audit_global_df = metric_long_df(joined_df, "global", global_metrics)
audit_event_df = metric_long_df(joined_df, "evento", base_metrics, ["evento"])
audit_tipo_evento_df = metric_long_df(joined_df, "tipo_evento", base_metrics, ["tipo_evento"])
audit_event_tipo_df = metric_long_df(joined_df, "evento_tipo_evento", base_metrics, ["evento", "tipo_evento"])

audit_df = (
    audit_global_df
    .unionByName(audit_event_df)
    .unionByName(audit_tipo_evento_df)
    .unionByName(audit_event_tipo_df)
)
audit_df.createOrReplaceTempView("audit_df")


# COMMAND ----------
# CELULA 14 - Persistencia opcional e exibicao final

if OUTPUT_FINAL_TABLE:
    final_df.write.format("delta").mode("overwrite").saveAsTable(OUTPUT_FINAL_TABLE)

if OUTPUT_AUDIT_TABLE:
    audit_df.write.format("delta").mode("overwrite").saveAsTable(OUTPUT_AUDIT_TABLE)

if OUTPUT_ISSUES_TABLE:
    issues_df.write.format("delta").mode("overwrite").saveAsTable(OUTPUT_ISSUES_TABLE)

display(final_df)
display(audit_df)
display(issues_df.limit(100))
