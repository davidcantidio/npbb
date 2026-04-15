1 - sim
2 - os dois devem permanecer, pois um cpf pode estar ligado a mais de um evento ou ativação 

3 - dos dados internos do banco de dados do banco do branco, que vamos obter 

4 ) real  
5  - como sugeriu, 40 entra em 18-40  
6 - sim , exatamente iguais 
7 - 11 digitos sempre 
escolher so a linha mais recente dos dados do banco em caso de duplicidade de cpf ,

pode ser idade simulada e não real, se isso for facilitar as coisas . cod_sexo está no dataframe que reflete o banco de dados do banco do brasil 

3 -

cliente = false - sim 
cod_sexo = null - se não houver campo 'sexo' na fonte de dados a se cruzar, caso  haja, manteremos 
data_nascimento = null  - caso não haja esse campo na nossa fonte de dados, caso haja, deve manter. 
Soma de idade = null  - só se não for cliente do banco e não houver informação sobre data de nascimento nos dados dos leads

o mesmo para faixa etária.



talvez seja importante estabelecer que a fonte de dados dos leads que recebemos de evento podem não foram enviadas no presente inicial como por exemplo a data de nascimento e sexo em gênero. 

4 - ) como achar melhor 

5 - sim, booleano 



que mais duvidas você tem ? 
1 - seguimos com sua sugest]ap 

2  )  Se o CPF tiver menos de 11 digitos,  adiciona zero a esquerda, e faz a verificação de digito do Cpf para verificar se ele é válido, se for considera, se não for, isso precisa ser contabilizado pois precisamos relatar  os dados que são inválidos,  quantidade de cpf invalido, data de nascimento inválida, isso precisa ser previsto e eu nao aviasie antees

2- antes falei que cod_sexo vinha com os dados do dataframe, mas acabei de saber que podem naõ vir, isso é  obtido com o cruzamento de outra fonte de dados que nao esta no escopo atual 


o notebook entrega um dataframe que será fonte de dados para um dashboard no powerbi 

de resto podemos seguir conforme suas sugestões 


tenho esse desenho do projeto, mas queria que você avaliasse e incrementasse trazendo  informações direcionadas baseadas nos esquemas de arquivos a serem cruzados, e o arquivo final esperado, para guiar a pessoa que vai criar o notebook. 



Seu plano, ao final deve ser um roadmap claro para a criação do notebook, a prova de falhas, com lógica impecável, afinal não trata-se de um cruzamento complexo. TEnha em mente meu objetivo final e os esquemas de dados fornecidos, pense em detalhes de lógica de programação que podem naõ ter sido abordadas aqui 



# Desenho Final — Notebook de Enriquecimento de Leads

> Versão fechada. Este documento descreve o comportamento esperado do notebook antes da implementação.

---

## 0. Objetivo Macro

**Entregar ao Power BI uma tabela linha a linha de leads por evento, com os campos de perfil (data de nascimento, faixa etária, flag de cliente) enriquecidos a partir do cadastro do banco, para que análises de público sejam possíveis.**

Tudo neste notebook existe para resolver esse problema. Validações, deduplicação e controles de qualidade estão aqui porque sem eles o dado chega errado no Power BI — não por rigor técnico pelo rigor em si.

---

## 1. Ambiente de Execução e Restrições

O notebook roda no **Databricks em ambiente corporativo** com as seguintes restrições que condicionam todas as escolhas técnicas:

| Restrição | Impacto |
|---|---|
| **Sem instalação de bibliotecas externas** | Não é possível usar pandas, validate-docbr, cpf ou qualquer pacote PyPI não homologado |
| **Somente PySpark e Spark SQL nativos** | Todas as transformações devem usar a API do Spark ou SQL puro |
| **Exceção permitida: Python UDF simples** | Lógica que não é expressável em SQL (ex: algoritmo de CPF) pode ser encapsulada em UDF Python puro, sem dependências externas |

### O que isso significa na prática

- Limpeza de CPF, conversão de datas, joins, deduplicação, derivações e auditoria: **tudo em Spark SQL / funções nativas do PySpark**.
- Validação dos dígitos verificadores do CPF: **única exceção**, implementada como UDF Python puro (aritmética simples, zero dependências externas).
- Nenhuma coleta local com .toPandas() exceto, se necessário, para exibir o dataframe de auditoria dentro do próprio notebook como visualização auxiliar.

---

## 2. Fontes de Dados

| Fonte | Papel | Chave |
|---|---|---|
| Base de leads/eventos | Base principal | cpf |
| Base do banco (cadastro) | Enriquecimento | cod_cpf_cgc |

Campos relevantes da base do banco: cod_cpf_cgc, dta_nasc_csnt, dta_ulta_atlz, dta_revisao, cod.

cod_sexo está **fora do escopo atual** por depender de fonte não disponível.

> **Formato de ingestão a confirmar antes da implementação:** os dados chegam como tabela Delta registrada no catálogo do Databricks, como CSV/Parquet em path de storage, ou via query em outro banco? Isso define apenas a célula de leitura — o restante do design não muda.

---

## 3. Padronização de CPF

Executada com funções nativas do Spark SQL, exceto a validação dos dígitos:

1. Remover todos os caracteres não numéricos: regexp_replace(cpf, '[^0-9]', '').
2. Completar com zeros à esquerda se necessário: lpad(cpf_limpo, 11, '0').
3. Validar os dois dígitos verificadores com **UDF Python puro** registrada no Spark — aritmética inteira, sem bibliotecas, única exceção às restrições do ambiente.
4. CPF com menos de 11 dígitos após limpeza, ou com dígitos verificadores inválidos, recebe flag cpf_valido = false.
5. **CPF inválido não participa de join válido.**
6. **CPF inválido entra no controle de qualidade** com sua flag.

---

## 4. Regra de Duplicidade

### 4.1 Leads/Eventos

- Duplicidade de CPF na base de leads é **permitida**: todas as linhas são mantidas.
- Cada linha representa uma ocorrência independente de lead/evento.

### 4.2 Base do Banco

- Duplicidade de CPF no banco é resolvida por **deduplicação antes do join**.
- Implementada com ROW_NUMBER() OVER (PARTITION BY cod_cpf_cgc ORDER BY ...) em Spark SQL puro.
- Critério de ordenação (decrescente):
  1. dta_ulta_atlz DESC
  2. dta_revisao DESC
  3. cod DESC
- Apenas a linha com row_num = 1 por CPF é mantida para o cruzamento.

---

## 5. Cruzamento

- Tipo: **LEFT JOIN** da base de leads sobre a base do banco deduplicada.
- Chave: cpf (leads) ↔ cod_cpf_cgc (banco), ambos já padronizados.
- A condição de join inclui cpf_valido = true no lado dos leads, garantindo que CPF inválido nunca gere match.
- Implementado em Spark SQL puro.

---

## 6. Validação de data_nascimento

Executada com funções nativas do Spark SQL (TRY_CAST, to_date, current_date, literais de data). Nenhuma UDF necessária.

Um valor é considerado **inválido** se:

- Existe mas **não converte para data** — TRY_CAST(valor AS DATE) retorna null em caso de falha, sinalizando o problema sem lançar exceção.
- Converte, mas resulta em **data futura** (posterior à data de execução do notebook).
- Converte, mas resulta em **data anterior a 01/01/1900**.

Valores inválidos são tratados como ausentes para fins de derivação. Cada linha recebe flag dnasc_status com valores: valida, invalida, ausente.

---

## 7. Precedência de Campos

> **Banco prevalece. Lead é fallback.**

Implementado com COALESCE(campo_banco, campo_lead) em Spark SQL.

| Campo | Fonte primária | Fallback |
|---|---|---|
| data_nascimento | dta_nasc_csnt (banco) | campo equivalente no lead |
| demais campos sobrepostos | banco | lead |

---

## 8. Campos Calculados

Todos expressáveis em Spark SQL nativo.

### 8.1 cliente

| Condição | Valor |
|---|---|
| CPF válido com match no banco | true |
| CPF sem match ou inválido | false |

CASE WHEN banco.cod_cpf_cgc IS NOT NULL THEN true ELSE false END

### 8.2 cod_sexo

- Sempre null neste escopo. Campo mantido no layout para compatibilidade futura.

### 8.3 data_nascimento final

- COALESCE(dta_nasc_csnt_banco, data_nascimento_lead), onde cada lado já passou pela validação da seção 6.
- null somente quando não houver valor aproveitável em nenhuma fonte.

### 8.4 Soma de ano_evento

- YEAR(data_evento)

### 8.5 Soma de idade

- YEAR(data_evento) - YEAR(data_nascimento)
- null quando data_nascimento for nula.

### 8.6 faixa_etaria

CASE WHEN em Spark SQL:

| Condição | Valor |
|---|---|
| Soma de idade < 18 | <18 |
| 18 ≤ Soma de idade ≤ 40 | 18-40 |
| Soma de idade > 40 | 40+ |
| Soma de idade é nula | Desconhecido |

> O valor 40 **entra em 18-40**.

---

## 9. Layout Final do Dataframe de Saída

Colunas exatamente nesta ordem e com estes nomes, selecionadas explicitamente no SELECT final:

| # | Coluna |
|---|---|
| 1 | evento |
| 2 | data_evento |
| 3 | Soma de ano_evento |
| 4 | cliente |
| 5 | cod_sexo |
| 6 | cpf |
| 7 | data_nascimento |
| 8 | faixa_etaria |
| 9 | Soma de idade |
| 10 | local |
| 11 | tipo_evento |

---

## 10. Controle de Qualidade (Dataframe de Auditoria)

Calculado via agregações Spark SQL sobre as flags geradas nas etapas anteriores. Nenhuma biblioteca extra necessária.

| Métrica |
|---|
| Total de registros de leads |
| Total de CPFs válidos |
| Total de CPFs inválidos |
| Total de CPFs encontrados no banco |
| Total de CPFs não encontrados no banco |
| Total de data_nascimento ausente no lead |
| Total de data_nascimento inválida no lead |
| Total de data_nascimento preenchida pelo banco |
| Total de data_nascimento final nula |
| Total por evento |
| Total por tipo de evento |

Este dataframe é exibido como tabela dentro do próprio notebook para inspeção. Não precisa sair para o Power BI.

---

## 11. Estrutura Lógica do Notebook (Seções/Células)


1. Ingestão
   └── Leitura da base de leads      [Spark — formato a confirmar]
   └── Leitura da base do banco      [Spark — formato a confirmar]

2. Padronização
   └── Normalização de nomes de colunas esperadas
   └── Limpeza de CPF (regexp_replace + lpad)   [Spark SQL nativo]
   └── Conversão de colunas de data (to_date)   [Spark SQL nativo]

3. Validação
   └── Validação dos dígitos verificadores do CPF   [UDF Python puro — única exceção]
   └── Classificação de data_nascimento             [Spark SQL: TRY_CAST + comparações]
   └── Geração de flags de qualidade por linha      [Spark SQL: CASE WHEN]

4. Deduplicação do banco
   └── ROW_NUMBER() OVER (PARTITION BY cpf ORDER BY ...)   [Spark SQL nativo]
   └── Filtro WHERE row_num = 1

5. Cruzamento
   └── LEFT JOIN leads ← banco dedupado   [Spark SQL nativo]
   └── Condição de join inclui cpf_valido = true

6. Reconciliação
   └── COALESCE(banco, lead) por campo   [Spark SQL nativo]
   └── Definição do campo cliente        [CASE WHEN]

7. Derivações
   └── Soma de ano_evento   [YEAR()]
   └── Soma de idade        [YEAR() - YEAR()]
   └── faixa_etaria         [CASE WHEN]

8. Saída
   └── SELECT explícito com os 11 campos na ordem correta → dataframe final
   └── Agregações das flags → dataframe de auditoria


---

## 12. Decisões Fora do Escopo

| Item | Status |
|---|---|
| cod_sexo | Fora do escopo — fonte indisponível |
| Agregações analíticas | Fora do escopo — responsabilidade do Power BI |
| Deduplicação de leads | Fora do escopo — todas as linhas são mantidas |
| Persistência do resultado | A definir — gravar como tabela Delta ou expor via path depende da integração com o Power BI no ambiente corporativo |

Quero, seja detalhista, antecipe erros, quero uma versão a prova de erros voce tem todas as informações pra isso 
Quero, atente para não perder nenhuma informação no processo