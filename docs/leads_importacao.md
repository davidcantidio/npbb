# Importacao de Leads (CSV/XLSX)

## Objetivo
Importar leads via CSV/XLSX com mapeamento assistido, aliases e tratamento de datetime.

## Endpoints
- `GET /leads`  
  Lista leads paginados (`page`, `page_size`) com campos principais e a conversao mais recente
  (`evento_convertido_id`, `evento_convertido_nome`, `tipo_conversao`, `data_conversao`).
- `POST /leads/import/upload`  
  Valida arquivo (extensao/tamanho).
- `POST /leads/import/preview`  
  Retorna headers, amostra, `start_index`, `suggestions`, `samples_by_column`, `alias_hits`.
- `POST /leads/import/validate`  
  Valida mapeamento (exige email ou CPF).
- `POST /leads/import`  
  Executa import com mapeamento confirmado.
- `GET /leads/referencias/*`  
  Opcoes canonicas (eventos, cidades, estados, generos).
- `GET/POST /leads/aliases`  
  Lookup e persistencia de alias.

## Regras principais
- Campos essenciais: **email ou CPF**.
- Colunas sem correspondencia podem ser **ignoradas**.
- Campos mapeaveis adicionais (opcionais):
  - Endereco: `endereco_rua`, `endereco_numero`, `bairro`, `cidade`, `estado`, `cep`
  - Perfil: `genero`
  - Compra: `codigo_promocional`, `ingresso_tipo`, `ingresso_qtd`
- Heuristicas e pesos seguem o catalogo do PRD (ver `docs/leads_conversoes.md`).
- Auto-selecao:
  - So ocorre quando a amostra tem **>= 3** valores validos.
  - Confianca automatica e **capada em 0.9**.
- Dedupe (chave unica):
  - Regra: **email + cpf + evento_nome + sessao** (quando aplicavel).
  - Quando email ou cpf estiverem vazios, usa o campo disponivel.
  - Duplicidade no mesmo lote: **mantem a ultima ocorrencia**.
- Upsert (politica):
  - Atualiza apenas **campos nao-nulos** do import.
  - Campos existentes nao sao sobrescritos por valores vazios.
- Batch size:
  - Valor padrao: **500** registros por lote.
- Limite de upload:
  - Tamanho maximo do arquivo controlado por `LEADS_IMPORT_MAX_BYTES` (padrao **50MB**).
  - Para uploads grandes em dev, recomenda-se iniciar o uvicorn com `--timeout-keep-alive 120`.
- Resumo final:
  - O retorno inclui `summary` com `filename`, `total`, `created`, `updated`, `skipped`, `errors`.
  - `errors` corresponde ao total de linhas ignoradas por erro durante o import.
- Enriquecimento opcional por CEP:
  - Quando habilitado (`enriquecer_cep=true`), o sistema tenta preencher
    rua/bairro/cidade/estado a partir do CEP.
  - Falhas na consulta nao bloqueiam o import.
- Aliases:
  - Valores confirmados viram alias para imports futuros.
  - Campos suportados: evento, cidade, estado, genero.
- Datetime:
  - Mantem `data_compra` (datetime).
  - Separa em `data_compra_data` e `data_compra_hora` quando aplicavel.

## Fluxo esperado
1) Usuario envia arquivo.
2) Sistema detecta linha de dados e sugere mapeamento.
3) Usuario confirma mapeamento e referencias.
4) Import executa, retornando resumo (criadas/atualizadas/ignoradas).
5) UI recarrega a listagem de leads e exibe a tabela atualizada.

## Resposta de listagem (`GET /leads`)
- Estrutura:
  - `page`, `page_size`, `total`, `items[]`.
- Cada item inclui, entre outros:
  - Identificacao e contato: `id`, `nome`, `email`, `cpf`, `telefone`.
  - Origem: `evento_nome`, `cidade`, `estado`.
  - Conversao mais recente: `evento_convertido_id`, `evento_convertido_nome`,
    `tipo_conversao`, `data_conversao`.
  - Datas: `data_compra`, `data_criacao`.
