---
doc_id: "ADR-IMPORTACAO-LEADS-OWNERSHIP-POR-CONTEXTO"
version: "1.0"
status: "proposed"
owner: "Eng"
last_updated: "2026-04-15"
scope_ref: "FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD"
---

# ADR: ownership por contexto na importacao de leads

## Status

Proposto

## Contexto

Hoje existem dois fluxos paralelos de importacao de leads:

1. batch classico com `LeadBatch.evento_id` e `LeadSilver.evento_id`;
2. ETL com `snapshot.evento_id`.

Mesmo assim, partes do sistema continuam tratando campos owned pelo Evento como
se fossem input da linha:

- no classico, `data_evento` ainda vem de `dados_brutos` e gera DQ por linha;
- no ETL, o vinculo canonico do evento ainda depende de `evento_nome`.

O resultado e uma mistura de fontes de verdade, com erro de escopo na DQ e
risco de vinculo incorreto.

## Decisao

Quando a importacao estiver ancorada em `evento_id`, o sistema deve operar com
**ownership por contexto**:

- campos owned pelo Evento devem ser derivados do cadastro do `Evento`;
- campos owned pela linha devem continuar vindo do arquivo;
- a UI e a DQ devem refletir essa separacao.

### Campos locked como owned pelo Evento

- `evento`
- `tipo_evento`
- `data_evento`

### Politica de `data_evento`

- data canonica:
  `data_inicio_realizada`, senao `data_inicio_prevista`
- ausencia de data canonica:
  problema unico de dados mestres ou configuracao do lote
- proibido:
  transformar ausencia ou formato invalido do cadastro em `N` linhas invalidas

### ETL

- o vinculo canonico do evento no commit deve usar `snapshot.evento_id`
- `evento_nome` pode continuar existindo como dado textual de origem e para
  compatibilidade, mas nao como mecanismo primario de resolucao canonica

### Campos ainda em aberto

`local`, `cidade` e `estado` permanecem em aberto nesta ADR. O diagnostico
mostrou sobrecarga semantica entre localidade do evento e atributos do lead.
Esses campos exigem fechamento de contrato antes de uma remediacao ampla.

## Alternativas consideradas

### 1. Manter dual sourcing atual

Rejeitada.

Mantem erro arquitetural: o sistema sabe qual e o evento do lote, mas continua
aceitando que a planilha dite partes do evento e gere DQ por linha.

### 2. Enriquecer o CSV intermediario, mas continuar validando a planilha como origem

Rejeitada.

So mascara o problema. Se o contexto do evento ja esta fixado, o campo nao deve
ser tratado como input do operador.

### 3. Separar ownership por contexto

Escolhida.

E a unica alternativa que alinha contrato, pipeline, persistencia e UI.

## Consequencias

### Positivas

- elimina falso positivo de DQ para `data_evento` em lote com evento fixo
- remove risco de resolucao canonica incorreta por nome no ETL
- cria uma regra simples para extensoes futuras: com `evento_id`, Evento manda

### Negativas

- exige tornar a UI contextual
- pode expor que `local` / `cidade` / `estado` nao tem semantica fechada hoje
- pode pressionar uma remediacao estrutural futura na chave de dedupe

## Implementacao recomendada

1. materializacao classica deriva `data_evento` do `Evento`
2. pipeline/status UI nao culpam a planilha por campo derivado
3. ETL commit persiste o vinculo canonico usando `snapshot.evento_id`
4. remediacao de `local` / `cidade` / `estado` entra apenas com contrato
   explicitado
