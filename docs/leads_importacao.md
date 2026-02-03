# Importacao de Leads (README curto)

## Objetivo
Importar leads via CSV/XLSX com mapeamento assistido, aliases e tratamento de datetime.

## Endpoints
- `POST /leads/import/upload`  
  Valida arquivo (extensao/tamanho).
- `POST /leads/import/preview`  
  Retorna headers, amostra, `start_index`, `suggestions`, `samples_by_column`, `alias_hits`.
- `POST /leads/import/validate`  
  Valida mapeamento (exige email ou CPF).
- `POST /leads/import`  
  Executa import com mapeamento confirmado.
- `GET /leads/referencias/*`  
  Opcoes canônicas (eventos, cidades, estados, generos).
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
  - Se apenas **email** ou **CPF** existir, o dedupe usa o campo disponivel.
- Politica de atualizacao por campo (baseline):
  | Campo | Estrategia |
  | --- | --- |
  | Identificacao (`email`, `cpf`) | **Nao sobrescreve** se ja existe; preenche apenas quando o campo estiver vazio. |
  | Nome/perfil (`nome`, `sobrenome`, `genero`, `data_nascimento`) | Atualiza se novo valor for nao-nulo. |
  | Contato/endereco (`telefone`, `endereco_*`, `cidade`, `estado`, `cep`) | Atualiza se novo valor for nao-nulo. |
  | Compra (`evento_nome`, `sessao`, `data_compra*`, `ingresso_*`, `codigo_promocional`, `metodo_entrega`) | Atualiza se novo valor for nao-nulo. |
  | Fonte (`fonte_origem`) | Mantem a **primeira fonte registrada**; nao sobrescreve em imports futuros. |
- Batch size:
  - Valor padrao: **500** registros por lote.
- Limite de upload:
  - Tamanho maximo do arquivo controlado por `LEADS_IMPORT_MAX_BYTES` (padrao **50MB**).
  - Para uploads grandes em dev, recomenda-se iniciar o uvicorn com `--timeout-keep-alive 120`.
- Resumo por lote:
  - O retorno inclui `batches` com resultados por lote.
  - Para evitar payload grande, o resumo e limitado por `LEADS_IMPORT_BATCH_SUMMARY_LIMIT` (padrao **200**).
- Resumo final:
  - O retorno inclui `summary` com `filename`, `total`, `created`, `updated`, `skipped`, `errors`.
  - `errors` corresponde ao total de linhas ignoradas por erro durante o import.
- Limites e truncamento:
  - Valores de texto sao **truncados** automaticamente quando excedem o limite do banco.
  - Ex.: `endereco_numero` e limitado a 120 caracteres.
  - O import continua sem falhar, e o truncamento gera log interno.
- Enriquecimento opcional por CEP:
  - Quando habilitado (`enriquecer_cep=true`), o sistema tenta preencher
    rua/bairro/cidade/estado a partir do CEP.
  - Usa cache interno para reduzir chamadas externas.
  - Falhas na consulta nao bloqueiam o import.
- Aliases:
  - Valores confirmados viram alias para imports futuros.
  - Campos suportados: evento, cidade, estado, genero.
- Datetime:
  - Mantem `data_compra` (datetime).
  - Separa em `data_compra_data` e `data_compra_hora` quando aplicavel.
- Indices recomendados (performance):
  - `(email, cpf, evento_nome, sessao)`: acelera dedupe/upsert.
  - `data_compra`: acelera filtros por periodo.
  - `estado`, `cidade`: acelera rankings e filtros geograficos.
  - `fonte_origem`: acelera filtros por origem.

## Fluxo esperado
1) Usuario envia arquivo.
2) Sistema detecta linha de dados e sugere mapeamento.
3) Usuario confirma mapeamento e referencias.
4) Import executa, retornando resumo (criadas/atualizadas/ignoradas).
