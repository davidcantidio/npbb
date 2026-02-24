# Inventario de Fontes (Pasta de Trabalho)

Este inventario cobre os arquivos encontrados na pasta de trabalho do fechamento. O objetivo e registrar o que existe, o que cada arquivo contem, e quais campos/metadados sao extraiveis para o banco.

## Mapa de arquivos (source_id -> arquivo no disco)

- SRC_DOCX_MODELO -> Fechamento_TMJB2025_Modelo_NPBB_v2.docx
Fonte: arquivo de referencia | local: nome do arquivo | evidência: documento modelo fornecido
- SRC_PDF_ACESSO_DIURNO_GRATUITO_DOZE -> 12.12 gratuito - controle de acesso.pdf
Fonte: pasta de trabalho | local: listagem do diretorio | evidência: nome do arquivo
- SRC_PDF_ACESSO_NOTURNO_TREZE -> 13.12 - Controle de Acesso.pdf
Fonte: pasta de trabalho | local: listagem do diretorio | evidência: nome do arquivo
- SRC_PDF_ACESSO_DIURNO_GRATUITO_TREZE -> 13.12 Gratuito - Controle de Acesso.pdf
Fonte: pasta de trabalho | local: listagem do diretorio | evidência: nome do arquivo
- SRC_PDF_ACESSO_DIURNO_GRATUITO_QUATORZE -> 14.12 gratuito - Controle de Acesso.pdf
Fonte: pasta de trabalho | local: listagem do diretorio | evidência: nome do arquivo
- SRC_PDF_DIMAC_MONITORAMENTO -> DIMAC - TMJ 25 - RELATÓRIO DE MONITORAMENTO - REVISADO.pdf
Fonte: pasta de trabalho | local: listagem do diretorio | evidência: nome do arquivo
- SRC_PDF_MTC_IMPRENSA -> MTC_Relatorio_TMJBB_2025- MTC.pdf.pdf
Fonte: pasta de trabalho | local: listagem do diretorio | evidência: nome do arquivo
- SRC_XLSX_LEADS_FESTIVAL_ESPORTES -> LEADS FESTIVAL DE ESPORTES 25.xlsx
Fonte: pasta de trabalho | local: listagem do diretorio | evidência: nome do arquivo
- SRC_XLSX_OPTIN_ACEITOS_DOZE -> TAMO JUNTO BB 12.12 - 01.1 - Opt-In Aceitos.xlsx
Fonte: pasta de trabalho | local: listagem do diretorio | evidência: nome do arquivo
- SRC_XLSX_OPTIN_ACEITOS_TREZE -> TAMO JUNTO BB 13.12 - Opt-In POR EVENTO (aceitos)v5.xlsx
Fonte: pasta de trabalho | local: listagem do diretorio | evidência: nome do arquivo
- SRC_PPTX_MIDIAS_SOCIAIS -> Relatorio TMJ BB  (Fortaleza)_V1.pptx
Fonte: pasta de trabalho | local: listagem do diretorio | evidência: nome do arquivo

Nota: o documento modelo (DOCX) esta fora da pasta de trabalho; ele e a referencia primaria de estrutura do relatorio.

## Inventario (o que contem e o que extrair)

| source_id | tipo | datas/sessoes cobertas (inferido) | o que contem | campos extraiveis (exemplos) | limitacoes / cuidados |
|---|---|---|---|---|---|
| SRC_DOCX_MODELO | DOCX | Modelo (spec) | Estrutura do relatorio: secoes, figuras, metricas e definicoes | Titulos de secoes, lista de figuras, tabela de controle de acesso, definicoes e limitacoes | Documento e "fonte de requisitos"; valores numericos dentro dele nao sao fonte primaria dos dados, mas sim do fechamento |
| SRC_PDF_ACESSO_DIURNO_GRATUITO_DOZE | PDF | Dia doze (diurno, gratuito) | Controle de acesso por sessao (entradas validadas e derivados) | `session_name`, `session_start_at`, contagens de validos/invalidos/bloqueados/presentes/ausentes, taxa de comparecimento | Sem deduplicacao de pessoas; fonte em PDF exige extractor de tabela; validar consistencia entre colunas |
| SRC_PDF_ACESSO_DIURNO_GRATUITO_TREZE | PDF | Dia treze (diurno, gratuito) | Controle de acesso por sessao (entradas validadas e derivados) | Mesmos campos do controle de acesso | Mesmo cuidado: sem publico unico; PDF pode ter layout variavel |
| SRC_PDF_ACESSO_NOTURNO_TREZE | PDF | Dia treze (noturno, show) | Controle de acesso por sessao do show (entradas validadas e derivados) | Mesmos campos do controle de acesso; dimensao `session_type=show` | Classificacao "show" deve ser confirmada no conteudo; sem isso, tratar como sessao generica ate validar |
| SRC_PDF_ACESSO_DIURNO_GRATUITO_QUATORZE | PDF | Dia quatorze (diurno, gratuito) | Controle de acesso por sessao (entradas validadas e derivados) | Mesmos campos do controle de acesso | Idem: sem deduplicacao; risco de ausencia de sessao noturna (show) nesta pasta |
| SRC_XLSX_OPTIN_ACEITOS_DOZE | XLSX | Sessao de show do dia doze (horario noturno) | Transacoes/ingressos com opt-in aceito (Eventim) | `evento`, `sessao`, `dt_hr_compra`, `opt_in_flag`, `canal_venda`, `metodo_entrega`, dados do titular (cpf/email), endereco, genero, codigo_promocional, tipo de ingresso, quantidade | Recorte: apenas opt-in aceitos; contem PII (LGPD); header com celulas mescladas exige normalizacao de colunas |
| SRC_XLSX_OPTIN_ACEITOS_TREZE | XLSX | Sessao de show do dia treze (horario noturno) | Transacoes/ingressos com opt-in aceito (Eventim) | Mesmos campos do XLSX de opt-in | Mesmo recorte e cuidados; validar consistencia de nomes de colunas entre arquivos |
| SRC_XLSX_LEADS_FESTIVAL_ESPORTES | XLSX | Festival de esportes (ativacoes diurnas) | Cadastros de leads e atributos (inclui acao/ativacao) | Nome/sobrenome, CPF, email, telefone, evento, data criacao, acoes, interesses, area atuacao, promotor | PII; dedupe por CPF e/ou email; a coluna de acoes pode conter multiplos valores (precisa explodir) |
| SRC_PPTX_MIDIAS_SOCIAIS | PPTX | Periodo de midias sociais do evento | Metricas de Instagram e highlights de social listening; benchmarks e comparativos | Metricas por periodo, formatos, conteudos de destaque, menções por plataforma, sentimento, insights | PPTX e semantico: numeros em boxes; requer extracao por slide + mapeamento slide->metrica e registro de evidencias |
| SRC_PDF_DIMAC_MONITORAMENTO | PDF | Dias do evento (perfil e percepcao) | Perfil, satisfacao e percepcao (survey) | Tabelas e graficos de distribuicao, percentuais por pergunta, possivel metodologia e amostra | PDF pode estar como imagem; se nao houver tabela extraivel, exigir extracao assistida ou microdados |
| SRC_PDF_MTC_IMPRENSA | PDF | Periodo de imprensa | Release, insercoes, entrevistas, equivalencia publicitaria e distribuicao por canal | Contagens agregadas e, idealmente, lista detalhada de insercoes (se existir no arquivo) | Se o PDF trouxer apenas resumo, pedir base detalhada para auditoria e reuso |

## Detalhe (XLSX)

### SRC_XLSX_LEADS_FESTIVAL_ESPORTES

- Aba encontrada: Entidades
- Chaves provaveis:
  - `CPF` (identificador forte para dedupe)
  - `Email` (backup para dedupe)
  - `DataCriacao` (carimbo temporal)
- Colunas observadas (header):
  - `Nome`, `Sobrenome`, `RG`, `CPF`, `Sexo`, `Email`, `Telefone`
  - `Evento`
  - `CPFPromotor`, `NomePromotor`
  - `DataNascimento`, `Cep`, `Estado`, `Cidade`
  - `DataCriacao`
  - `Acoes`, `Interesses`, `AreaAtuacao`

### SRC_XLSX_OPTIN_ACEITOS_DOZE e SRC_XLSX_OPTIN_ACEITOS_TREZE

- Aba encontrada: 01.1 - Opt-In Aceitos
Fonte: arquivos de opt-in | local: lista de abas | evidência: nome da aba
- Header observado (linha de cabecalho contem celulas mescladas e lacunas). Recomendacao: criar um dicionario de mapeamento de colunas (original -> canonical) e preencher lacunas por contexto.
- Chaves provaveis:
  - `CPF` (titular)
  - `Dt e Hr Compra` (timestamp de compra)
  - `SESSAO` (timestamp da sessao)
  - `Cod Promocional` (identificador de transacao/cupom, quando aplicavel)
- Grupos de campos observados:
  - Identificacao do evento e sessao
  - Dados de compra e opt-in
  - Canal de venda e metodo de entrega
  - Dados do titular (nome/sobrenome/email/cpf)
  - Endereco e contato
  - Dados demograficos basicos
  - Tipo de ingresso e quantidade

## Detalhe (PPTX)

- Principais secoes identificadas por titulos de slide (normalizado):
  - Contexto
  - Objetivo
  - Big numbers
  - Dados de perfil (Instagram)
  - Conteudos de destaque
  - Comentarios
  - Desempenho de perfis
  - Formatos dos conteudos
  - Gatilhos emocionais e insights
  - Redes externas (social listening)
