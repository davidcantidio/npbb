# Arquitetura de ETL (raw -> staging -> canonical -> marts/report)

Objetivo: criar capacidade repetivel de extrair fontes heterogeneas (PDF/XLSX/PPTX), padronizar em um modelo canonico, carregar no banco e gerar o relatorio Word automaticamente, com rastreabilidade por metrica.

## Camadas do pipeline

- raw:
  - Copia imutavel dos arquivos originais (com hash).
  - Registro em `sources` (metadados) e `ingestions` (execucao).
- staging:
  - Extracao "o mais fiel possivel" ao layout da fonte.
  - Pouca interpretacao; foco em preservacao de colunas e valores.
  - Persistencia em tabelas `stg_*` ou arquivos parquet/csv versionados.
- canonical:
  - Normalizacao de chaves (evento, sessao, datas), dominios e nomes de colunas.
  - Aplicacao de regras (ex.: sessao->tipo, mapeamento de segmento, hashing de PII).
  - Carga nas tabelas canonicas (ex.: `event_sessions`, `attendance_access_control`, `optin_transactions`).
- marts/report:
  - Views/tabelas agregadas prontas para o relatorio (ex.: `mart_report_*`).
  - Validacoes de reconciliacao e consistencia.

## Estrategia por tipo de fonte

### XLSX (Eventim opt-in, leads)

- Extracao:
  - `openpyxl` para leitura confiavel de abas e celulas.
  - Detectar header multi-linha / celulas mescladas e construir colunas canonicas.
- Normalizacao:
  - Datas: separar `purchase_at`, `purchase_date`, `purchase_time`.
  - Sessao: mapear timestamp/nome para `event_sessions`.
  - PII: aplicar hashing para `person_key_hash` e minimizar campos persistidos conforme necessidade.
- Validacoes:
  - Dedupe por chaves (cpf/email + evento + sessao).
  - Nulos criticos em chaves.
  - Consistencia entre `ticket_qty` e agregados.

### PPTX (midias sociais / social listening)

- Extracao:
  - Preferencial: `python-pptx` para ler shapes, tabelas e textos por slide.
  - Fallback: parse do arquivo como zip + xml (extrair `a:t` e mapear por slide).
- Mapeamento:
  - Tabela de configuracao "slide -> metrica" com:
    - `metric_name`
    - `platform`
    - periodo (quando existir no slide)
    - regra de extracao (regex, posicao, label)
- Linhagem:
  - Para cada metrica, registrar `source_id`, `slide_title`, e identificador do box/texto.
- Validacoes:
  - Metricas com unidade/periodo obrigatorios.
  - Checar que o mesmo `metric_name` nao muda de definicao entre versoes do PPTX.

### PDF (controle de acesso, DIMAC, MTC)

- Extracao:
  - Tabelas: `pdfplumber`/`camelot`/`tabula` (quando o PDF for texto/tabela).
  - Se for imagem/scan: OCR (fluxo separado) ou extracao assistida.
  - Estrategia de fallback obrigatoria:
    - "extracao assistida com marcacao manual": usuario marca a tabela/area e salva um "spec de extracao" (ex.: coordenadas ou tabela exportada).
- Normalizacao:
  - Controle de acesso: padronizar colunas (validos/invalidos/bloqueados/presentes/ausentes/comparecimento).
  - DIMAC: padronizar "pergunta/opcao/valor" e metadados da amostra.
  - MTC: padronizar metricas agregadas e (se houver) detalhamento de insercoes.
- Linhagem:
  - Registrar `page_number` e titulo da tabela/figura para cada valor extraido.
- Validacoes:
  - Reconciliar totais (ex.: presentes + ausentes vs validos quando aplicavel).
  - Detectar mudanca de layout (colunas faltantes, header diferente).

## Linhagem (anti-alucinacao)

- Principio: nenhum numero exibido no relatorio pode existir sem:
  - `source_id`
  - localizacao (pagina/slide/aba/range)
  - evidencia (titulo do quadro/tabela/label)
  - regra de calculo (query/view)

Implementacao sugerida:

- `metric_lineage` (ou colunas `lineage_ref` nos fatos) contendo:
  - `source_id`, `ingestion_id`
  - `location_type` (page, slide, sheet, range)
  - `location_value`
  - `evidence_text`

## Observabilidade e Data Quality

- Checks automaticos:
  - Esquema: colunas obrigatorias presentes.
  - Dominio: `session_type` valido, segmentos conhecidos.
  - Reconciliacao: derivados batem com base.
- Alertas:
  - Ingestao parcial (faltou pagina/slide).
  - Mudanca de layout detectada.
- Logs:
  - Guardar contagens de linhas carregadas por fonte e por sessao.

