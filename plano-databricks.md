# Notebook Databricks de Enriquecimento de Leads com Base BB

## Summary

- Objetivo: produzir um `final_df` linha a linha para o Power BI, preservando todas as linhas dos leads, enriquecendo por CPF a partir da base BB e gerando auditoria robusta.
- Contrato fechado: `cpf` e a unica coluna obrigatoria da fonte de leads; `cod_sexo` fica `null` nesta v1; duplicidade de CPF nos leads e preservada; duplicidade no BB e resolvida pela linha mais recente.
- Ajustes incorporados na revisao: `audit_df` tera metricas por linha e por CPF unico, valores de CPF irrecuperaveis para 11 digitos viram `null` no `final_df`, mas ficam preservados no staging e no `issues_df`, e `data 2.csv` vale como referencia de layout, nao como contrato literal de calculo.

## Public Interface

- Widgets/parametros obrigatorios: `lead_source_kind`, `lead_source_value`, `bank_source_kind`, `bank_source_value`.
- Widgets/parametros opcionais: `lead_delimiter` com default `,`, `lead_header` com default `true`, `lead_sheet_name` apenas se a origem suportar planilha/aba.
- Contrato de entrada dos leads: `cpf` obrigatorio; `evento`, `tipo_evento`, `local`, `data_evento`, `data_nascimento` opcionais.
- Normalizacao de cabecalhos: lowercase, trim, remocao de BOM, remocao de acentos e troca de separadores por `_`.
- Aliases aceitos sem decisao adicional do implementador: `evento_nome -> evento`, `dt_nascimento -> data_nascimento`, `sexo -> genero` apenas para deteccao e auditoria; `genero/sexo` nao alimenta `cod_sexo` nesta v1.
- Saida publica do notebook:
- `final_df` com colunas e ordem exatas: `evento`, `data_evento`, `Soma de ano_evento`, `cliente`, `cod_sexo`, `cpf`, `data_nascimento`, `faixa_etaria`, `Soma de idade`, `local`, `tipo_evento`.
- Tipos de `final_df`: `evento`, `local`, `tipo_evento`, `faixa_etaria`, `cod_sexo` e `cpf` como string, `cliente` boolean, `Soma de ano_evento` e `Soma de idade` integer, `data_evento` e `data_nascimento` como Spark `date`.
- `audit_df` em formato longo com colunas `escopo`, `evento`, `tipo_evento`, `metrica`, `valor`.
- Saida diagnostica opcional do notebook: `issues_df` por linha, com `__lead_row_id`, regra, severidade e valores crus relevantes; nao vai para Power BI, mas existe para nao perder rastreabilidade.

## Notebook Cells

1. **Celula 1 - Configuracao e imports**: criar widgets/parametros `lead_source_kind`, `lead_source_value`, `bank_source_kind`, `bank_source_value`, alem de opcionais como `lead_delimiter` e `lead_header`; importar `pyspark.sql.functions`, `Window` e registrar constantes de contrato.
Dica: definir logo aqui os nomes finais das 11 colunas e a data minima `1900-01-01`.

2. **Celula 2 - Leitura da fonte de leads**: ler a base de leads conforme o parametro de origem e sem descartar linhas; preservar exatamente o conteudo cru de entrada.
Dica: se a origem for CSV, fixar `encoding`, `header`, delimitador e inferencia controlada; evitar que Spark "adivinhe" tipos cedo demais.

3. **Celula 3 - Normalizacao de cabecalhos e contrato minimo**: normalizar nomes de colunas para lowercase, trim, sem acento e com `_`; aplicar aliases como `dt_nascimento -> data_nascimento` e `evento_nome -> evento`; validar que `cpf` existe.
Dica: se `cpf` nao existir apos normalizacao e aliases, a execucao falha; se faltarem `evento`, `tipo_evento`, `local`, `data_evento` ou `data_nascimento`, criar as colunas com `null` e registrar a inconformidade.

4. **Celula 4 - Staging bruto com rastreabilidade**: adicionar `__lead_row_id` imutavel e preservar `__cpf_raw`, `__data_nascimento_raw`, `__data_evento_raw`, alem das colunas de negocio lidas.
Dica: esta celula e a garantia de "nao perder informacao"; nenhuma transformacao posterior pode apagar essas colunas auxiliares ate o final do notebook.

5. **Celula 5 - Registro da UDF de CPF**: registrar uma UDF Python pura apenas para validar digitos verificadores do CPF.
Dica: a UDF deve rejeitar CPFs com todos os digitos iguais e tambem o placeholder `12345678909`, alinhando o notebook com as regras ja usadas no repositorio.

6. **Celula 6 - Padronizacao e validacao de CPF nos leads**: limpar nao digitos, aplicar `lpad` para 11 apenas quando o comprimento for de 1 a 11, marcar invalido quando vazio, maior que 11, repetido ou com DV invalido.
Dica: separar claramente `cpf_digits_raw`, `cpf_normalizado_11`, `cpf_valido`, `cpf_issue_code`; isso simplifica o `audit_df` e o `issues_df`.

7. **Celula 7 - Parsing e validacao das datas dos leads**: parsear `data_nascimento` e `data_evento` com `coalesce` entre formatos suportados.
Dica: para `data_nascimento`, marcar invalida se nao parsear, se for futura ou anterior a `1900-01-01`; para `data_evento`, marcar invalida se nao parsear ou se for anterior a `1900-01-01`, mas nao invalidar por ser futura.

8. **Celula 8 - Shortlist de CPFs elegiveis para match**: gerar `lead_cpfs_matchable` com os CPFs validos e distintos vindos dos leads.
Dica: esta celula existe por performance; ela evita varrer a base BB inteira com logica pesada.

9. **Celula 9 - Leitura enxuta da base BB**: ler apenas `cod_tipo`, `cod_cpf_cgc`, `dta_nasc_csnt`, `dta_ulta_atlz`, `dta_revisao`, `cod`.
Dica: nao carregar colunas desnecessarias da tabela de `239.650.151` linhas.

10. **Celula 10 - Filtro tecnico da base BB**: restringir a base BB a `cod_tipo = 1`, normalizar `cod_cpf_cgc`, excluir candidatos com mais de 11 digitos e reduzir a base ao conjunto de CPFs presentes em `lead_cpfs_matchable`.
Dica: nao usar a UDF de CPF na base BB inteira; primeiro reduza pelo conjunto de chaves dos leads.

11. **Celula 11 - Validacao e deduplicacao da base BB**: validar o CPF BB ja filtrado e aplicar `row_number` por CPF normalizado, ordenando por `dta_ulta_atlz desc`, `dta_revisao desc`, `cod desc`.
Dica: tratar datas sentinela como `0001-01-01` como nulas; incluir um desempate deterministico final por hash da linha para evitar instabilidade.

12. **Celula 12 - Join leads <- BB**: executar `LEFT JOIN` dos leads sobre a base BB deduplicada, usando apenas leads com `cpf_valido = true` como candidatos a match.
Dica: o join deve preservar a cardinalidade dos leads; depois dele, validar que a contagem de `__lead_row_id` continua identica a entrada.

13. **Celula 13 - Reconciliacao dos campos**: definir `cliente`, reconciliar `data_nascimento` com precedencia do BB e manter `cod_sexo = null`.
Dica: `cliente = true` somente se houver match no BB; `data_nascimento_final = coalesce(dta_nasc_csnt_valida, data_nascimento_lead_valida)`.

14. **Celula 14 - Derivacoes de negocio**: calcular `Soma de ano_evento`, `Soma de idade` e `faixa_etaria`.
Dica: a idade e simulada por diferenca simples de ano, nao idade real; `faixa_etaria` deve ser exatamente `<18`, `18-40`, `40+`, `Desconhecido`.

15. **Celula 15 - Montagem do `final_df`**: projetar apenas as 11 colunas finais, na ordem exata, com aliases literais.
Dica: usar aliases com backticks para nomes com espaco, como `` `Soma de ano_evento` `` e `` `Soma de idade` ``; internamente use `date`, mas no select final pode converter `data_evento` e `data_nascimento` para timestamp a meia-noite se quiser maxima aderencia visual ao `data 2.csv`.

16. **Celula 16 - Montagem do `issues_df`**: criar um dataframe tecnico por linha com `__lead_row_id`, severidade, regra, valor cru e valor normalizado.
Dica: ele nao vai ao Power BI, mas e obrigatorio para cumprir o requisito de nao perder informacao e facilitar debugging operacional.

17. **Celula 17 - Montagem do `audit_df`**: gerar metricas globais e por `evento` e `tipo_evento`, em formato longo com `escopo`, `evento`, `tipo_evento`, `metrica`, `valor`.
Dica: o `audit_df` deve trazer sempre contagens por linha e por CPF unico quando a metrica envolver CPF.

18. **Celula 18 - Assercoes finais e exibicao**: validar invariantes e exibir `final_df`, `audit_df` e uma amostra do `issues_df`.
Dica: assercoes minimas: mesma quantidade de linhas entre input e `final_df`; unicidade de `__lead_row_id`; colunas finais exatamente na ordem contratada.

## Implementation Changes

- Criar um staging de leads com `__lead_row_id` unico e colunas cruas preservadas: `__cpf_raw`, `__data_nascimento_raw`, `__data_evento_raw`, alem das colunas originais lidas. Nenhuma linha de lead e descartada em nenhum momento.
- Se `cpf` nao existir apos a normalizacao e o alias mapping, o notebook falha imediatamente. Se faltarem `evento`, `tipo_evento`, `local`, `data_evento` ou `data_nascimento`, o notebook cria a coluna com `null` e registra a ausencia no `audit_df`.
- Regra de CPF dos leads:
- remover nao digitos;
- se comprimento entre 1 e 11, aplicar `lpad(..., 11, '0')`;
- se comprimento zero ou maior que 11, marcar invalido;
- rejeitar CPF com todos os digitos iguais;
- rejeitar `12345678909`;
- validar DV com UDF Python puro;
- `cpf_valido = false` impede match, mas a linha segue no `final_df`.
- Regra do `cpf` final:
- se o CPF limpado tiver ate 11 digitos, o valor final exibido e o normalizado de 11 digitos;
- se tiver mais de 11 digitos ou vier vazio, `cpf` no `final_df` fica `null` e o valor cru fica preservado no staging e no `issues_df`.
- Regra de datas:
- `data_nascimento` aceita parsing em `yyyy-MM-dd`, `yyyy-MM-dd HH:mm:ss`, `dd/MM/yyyy`, `dd/MM/yyyy HH:mm:ss`, `M/d/yyyy`, `M/d/yyyy H:m:s`;
- `data_nascimento` e invalida se vazia, nao parseavel, futura ou anterior a `1900-01-01`;
- `data_evento` usa os mesmos formatos, mas nao e invalidada por ser futura; so por ausencia, erro de parsing ou data absurda anterior a `1900-01-01`.
- Estrategia obrigatoria de performance para a base BB:
- projetar so `cod_tipo`, `cod_cpf_cgc`, `dta_nasc_csnt`, `dta_ulta_atlz`, `dta_revisao`, `cod`;
- gerar `lead_cpfs_matchable` a partir dos leads com `cpf_valido = true`, distintos;
- usar esse conjunto pequeno para reduzir a base BB antes da deduplicacao;
- nao aplicar UDF de CPF na tabela BB inteira.
- Regra da base BB:
- considerar apenas `cod_tipo = 1`;
- normalizar `cod_cpf_cgc` para string numerica e `lpad` ate 11 quando aplicavel;
- excluir candidatos com mais de 11 digitos, que sao tratados como CNPJ ou nao-CPF;
- tratar datas sentinela como `0001-01-01` como nulas para qualidade e ordenacao.
- Deduplicacao BB:
- `row_number` por CPF normalizado;
- ordem: `dta_ulta_atlz desc nulls last`, `dta_revisao desc nulls last`, `cod desc nulls last` e, por fim, `sha2(to_json(struct(...)), 256) desc` como desempate deterministico.
- Join e enriquecimento:
- `LEFT JOIN` leads -> BB deduplicada;
- condicao de match usa apenas `__lead_row_id` preservado no lado esquerdo e CPF normalizado valido;
- validar invariantes: `final_df.count() == leads_input.count()` e unicidade de `__lead_row_id` apos o join.
- Campos derivados:
- `cliente = true` somente se houve match no banco; caso contrario `false`;
- `cod_sexo = null` sempre, mesmo que a fonte de leads tenha `sexo` ou `genero`;
- `data_nascimento` final = `coalesce(dta_nasc_csnt_valida, data_nascimento_lead_valida)`;
- `Soma de ano_evento = year(data_evento)` sem agregacao alguma;
- `Soma de idade = year(data_evento) - year(data_nascimento)`; idade simulada, nao idade real;
- `faixa_etaria`: `<18`, `18-40`, `40+`, `Desconhecido`.
- O notebook so faz o `SELECT` final para as 11 colunas no ultimo passo; ate la, mantem staging, flags e rastreabilidade para evitar perda de informacao operacional.

## Regras Criticas

- `cpf` e a unica coluna obrigatoria da fonte de leads; ausencia dela aborta o notebook.
- Leads nunca sao deduplicados nem descartados por CPF invalido.
- CPF invalido nunca faz match com a base BB, mas continua no `final_df`.
- Se o CPF cru tiver mais de 11 digitos e nao puder entrar no contrato final, `final_df.cpf = null`; o valor cru permanece no staging e no `issues_df`.
- `cod_sexo` fica sempre `null` nesta versao, independentemente de existir `sexo` ou `genero` na origem.
- `data 2.csv` nao deve ser copiado literalmente quando contrariar as regras; por exemplo, valores como `4050` em `Soma de ano_evento` sao tratados como erro do exemplo, nao como comportamento do notebook.

## Audit DF

- Metricas globais obrigatorias: `total_rows`, `cpf_valid_rows`, `cpf_invalid_rows`, `cpf_valid_unique`, `cpf_invalid_unique`, `bb_match_rows`, `bb_match_unique`, `bb_no_match_rows`, `bb_no_match_unique`.
- Metricas de datas obrigatorias: `lead_dnasc_missing_rows`, `lead_dnasc_invalid_rows`, `lead_data_evento_missing_rows`, `lead_data_evento_invalid_rows`, `birthdate_filled_from_bb_rows`, `final_birthdate_null_rows`.
- Metricas de contrato obrigatorias: `missing_evento_rows`, `missing_tipo_evento_rows`, `missing_local_rows`, `cpf_gt_11_digits_rows`, `cpf_lpad_applied_rows`.
- Quebra obrigatoria: escopo global e escopo por `evento` e `tipo_evento`.

## Test Plan

- Com `aurea_tour_2025_hevert(in).csv`, o `final_df` deve ter exatamente `292` linhas.
- O notebook deve preservar linhas com CPF curto, validando apos `lpad`, e manter contabilizados os CPFs invalidos.
- O join com a base BB nao pode multiplicar linhas; a cardinalidade final deve ser igual a cardinalidade de entrada dos leads.
- A deduplicacao da base BB deve sempre escolher a linha mais recente pelo criterio acordado.
- `faixa_etaria` e colunas finais devem respeitar exatamente o layout definido no prompt.
- O `audit_df` deve mostrar tanto contagem por linha quanto por CPF unico para metricas de CPF.

## Assumptions

- O notebook e parametrico e nao grava saida automaticamente.
- `local`, `evento` e `tipo_evento` sao mantidos como vierem da fonte de leads; nao ha regra adicional de padronizacao textual nesta v1.
- Datas sao tratadas internamente como datas validas de negocio; a apresentacao final pode ser timestamp a meia-noite para maior aderencia visual ao exemplo.
- `issues_df` faz parte do entregavel tecnico do notebook, mesmo nao sendo consumido pelo Power BI.
