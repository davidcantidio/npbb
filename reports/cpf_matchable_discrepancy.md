# Diagnóstico da discrepância de CPFs elegíveis para match

## Resumo

O número `51.456` não representa o total de linhas tratadas do arquivo. No notebook, ele representa a contagem de `CPFs válidos e únicos` após a validação da célula 6 e o `distinct()` da célula 9.

A origem usada pelo notebook está definida como `main.main.leads_coluna_origem` em [notebook_origem1 1.ipynb](</C:/Users/NPBB/npbb/notebook_origem1 1.ipynb:79>). Nesta análise, a linhagem foi tratada como resolvida com base na confirmação do usuário de que essa tabela corresponde atualmente a `LEADS-v4-iso.csv`.

Como checagem local adicional, `LEADS-v4-iso.csv` e `LEADS-v4.csv` são idênticos byte a byte: ambos têm `7.676.042` bytes e o mesmo SHA-256 `c0315b6080e4a82b9158b111cebc70e6d056883adc43a8483341dc3e87dce6ff`.

## O que isso implica sobre a Gold

As rejeições por dígito verificador realmente seriam estranhas se `LEADS-v4-iso.csv` fosse o output final da Gold deste repositório. Pelo código atual, a Gold descarta CPF inválido antes de gravar o CSV final:

- a normalização marca `CPF_INVALIDO` quando `is_valid_cpf(cpf)` falha em [lead_pipeline/pipeline.py](/C:/Users/NPBB/npbb/lead_pipeline/pipeline.py:247)
- linhas com esse motivo entram em `invalid_records` e não são adicionadas a `normalized_rows` em [lead_pipeline/pipeline.py](/C:/Users/NPBB/npbb/lead_pipeline/pipeline.py:667)
- o CSV consolidado final é gravado a partir de `final_df`, depois desse descarte, em [lead_pipeline/pipeline.py](/C:/Users/NPBB/npbb/lead_pipeline/pipeline.py:770)
- o contrato da Gold ainda exige CPF com exatamente `11` dígitos no processado em [lead_pipeline/contracts.py](/C:/Users/NPBB/npbb/lead_pipeline/contracts.py:47)

Há um segundo sinal forte: `LEADS-v4-iso.csv` não tem o schema da saída final da Gold.

- `LEADS-v4-iso.csv` tem `9` colunas: `nome, cpf, data_nascimento, email, telefone, origem, evento, local, data_evento`
- a saída final esperada da Gold tem `34` colunas e inclui `tipo_evento`, `fonte_origem`, `cidade`, `estado` e outros campos em [lead_pipeline/constants.py](/C:/Users/NPBB/npbb/lead_pipeline/constants.py:1)
- no lugar de `fonte_origem`, o arquivo analisado tem `origem`, que não pertence ao contrato final da Gold

Conclusão operacional: mesmo que a tabela `main.main.leads_coluna_origem` esteja hoje carregada com `LEADS-v4-iso.csv`, esse arquivo se comporta como um staging simplificado para o notebook, não como o CSV consolidado final produzido pela Gold do repositório.

## Regra que produz `51.456`

O notebook faz duas etapas relevantes:

1. Em [notebook_origem1 1.ipynb](</C:/Users/NPBB/npbb/notebook_origem1 1.ipynb:293>), a célula 6:
   - remove qualquer caractere não numérico do CPF
   - calcula o tamanho em dígitos
   - aplica `lpad(..., 11, "0")` quando o tamanho está entre `1` e `11`
   - rejeita `CPF_EMPTY`, `CPF_GT_11`, `CPF_REPEATED_DIGITS`, `CPF_KNOWN_PLACEHOLDER` e `CPF_CHECK_DIGIT_INVALID`
   - marca `cpf_valido = true` apenas quando nenhuma dessas rejeições ocorre
2. Em [notebook_origem1 1.ipynb](</C:/Users/NPBB/npbb/notebook_origem1 1.ipynb:446>), a célula 9:
   - filtra `cpf_valido`
   - seleciona `cpf_normalizado_11`
   - aplica `distinct()`

Em outras palavras, a métrica é:

`CPFs únicos elegíveis para match = distinct(cpf_normalizado_11) where cpf_valido = true`

## Decomposição da contagem

Reprodução local do cálculo sobre `LEADS-v4-iso.csv`, fora do notebook, com a mesma regra de CPF:

| Etapa | Total |
|---|---:|
| Linhas do CSV | 57.793 |
| Linhas com `cpf_valido = true` | 52.296 |
| CPFs únicos elegíveis para match | 51.456 |
| Linhas rejeitadas por CPF | 5.497 |
| Linhas válidas removidas por deduplicação | 840 |
| Grupos de CPF válido repetido | 824 |

Fechamento da conta:

- `57.793 - 52.296 = 5.497` linhas rejeitadas pela validação de CPF
- `52.296 - 51.456 = 840` linhas válidas descartadas pelo `distinct()`
- `57.793 = 51.456 + 5.497 + 840`

## Tipos de rejeição encontrados

| `cpf_issue_code` | Linhas | Observação |
|---|---:|---|
| `CPF_CHECK_DIGIT_INVALID` | 5.451 | Principal causa da queda |
| `CPF_EMPTY` | 45 | CPF vazio |
| `CPF_REPEATED_DIGITS` | 1 | Ex.: `00000000000` |
| `CPF_GT_11` | 0 | Não apareceu no arquivo |
| `CPF_KNOWN_PLACEHOLDER` | 0 | `12345678909` não apareceu no arquivo |

Observações úteis:

- O arquivo tem `56.807` CPFs com `11` dígitos, `877` com `10` dígitos e `109` com `1` a `6` dígitos.
- O `lpad` não explica a maior parte da perda. Entre os CPFs curtos:
  - `24` CPFs de `10` dígitos ficaram válidos depois do `lpad`
  - `1` CPF de `4` dígitos ficou válido depois do `lpad`
  - o restante continuou inválido pelo dígito verificador

## Evidência amostral

### Rejeições

| Linha no CSV | `cpf_raw` | `cpf_normalizado_11` | Motivo |
|---|---|---|---|
| 9 | `0198427018` | `00198427018` | `CPF_CHECK_DIGIT_INVALID` |
| 65 | `0112300116` | `00112300116` | `CPF_CHECK_DIGIT_INVALID` |
| 67 | `999999` | `00000999999` | `CPF_CHECK_DIGIT_INVALID` |
| 300 | `` | `null` | `CPF_EMPTY` |
| 10352 | `0` | `00000000000` | `CPF_REPEATED_DIGITS` |

### Duplicidade entre CPFs válidos

Exemplo de CPF válido repetido, descartado pelo `distinct()`:

| `cpf_normalizado_11` | Ocorrências | Linhas no CSV |
|---|---:|---|
| `00153410035` | 3 | `4603`, `7156`, `7345` |
| `00239890094` | 3 | `4867`, `9037`, `9104` |
| `01105305007` | 3 | `3900`, `4326`, `5624` |

## O que não interfere nessa contagem

Esta contagem de `51.456` não depende de `data_evento`, `data_nascimento` nem do join com a base BB:

- A célula 8 só faz parsing de datas e valida que exista pelo menos uma `data_evento` válida; ela não filtra linhas para montar `lead_cpfs_matchable`.
- A shortlist é construída na célula 9 exclusivamente a partir de `cpf_valido` e `cpf_normalizado_11`.
- O join com a base BB só começa na célula 10, depois que a shortlist já foi fechada.

## Conclusão prática

Se o objetivo é explicar por que o notebook mostra `51.456`, a causa está fechada:

- ele rejeita `5.497` linhas por regra de CPF
- ele remove mais `840` linhas válidas porque a métrica é por CPF único, não por linha

Se a expectativa passar a ser `57.793` elegíveis, isso deixa de ser diagnóstico e vira mudança de regra. Para chegar perto desse número, seria necessário remover o `distinct()`, afrouxar a validação de CPF, ou ambos.
