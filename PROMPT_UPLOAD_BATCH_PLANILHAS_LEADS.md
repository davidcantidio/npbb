# Prompt de implementacao - upload batch de planilhas de leads (revisado)

Documento de handoff para implementar upload batch no fluxo Bronze com encaixe no desenho atual, sem criar arquitetura paralela desnecessaria.

## Resumo executivo

- Este documento revisado substitui a versao anterior.
- O objetivo da revisao e tornar a execucao mais objetiva e sem ambiguidades.
- Todos os requisitos normativos da versao anterior foram preservados.
- Escopo desta rodada: apenas documentacao, sem mudanca de codigo.

## Decisao arquitetural principal

- O backend atual persiste **um arquivo por `LeadBatch`** em `lead_batches.arquivo_bronze`.
- Portanto, a versao batch **nao deve inventar um novo formato monolitico multi-arquivo no backend** como primeira abordagem.
- A implementacao deve ser um **orquestrador batch no frontend**, onde cada linha da grade representa **um futuro `LeadBatch` independente**.
- No submit, o frontend cria **N lotes** chamando o contrato atual `POST /leads/batches` uma vez por arquivo/linha, mantendo mapping e pipeline Gold por `batch_id` exatamente como ja funcionam hoje.

## Baseline validada no projeto (estado atual confirmado)

- O shell canonico de importacao ja existe em `frontend/src/pages/leads/ImportacaoPage.tsx`.
- O upload Bronze single atual ja existe em `frontend/src/pages/leads/importacao/ImportacaoUploadStep.tsx`.
- O contrato de persistencia Bronze por arquivo ja existe via `createLeadBatch` (`frontend/src/services/leads_import.ts`) e `criar_batch` (`backend/app/routers/leads.py`).
- O catalogo de eventos e regras de bloqueio por ativacao ja existem (`listReferenciaEventos`, `supportsActivationImport`, `getActivationImportBlockReason`).
- Criacao rapida de evento ja existe e deve ser reutilizada (`QuickCreateEventoModal` + `createEvento(..., criar_ativacao_padrao_bb: true)`).
- Listagem e criacao de ativacoes ja existem e devem ser reutilizadas (`listEventoAtivacoes`, `createEventoAtivacao`).
- Fluxo de mapeamento/pipeline por `batch_id` ja existe e deve ser reaproveitado sem alteracao de contrato.
- Fluxo ETL (`preview/commit`) ja coexiste no shell e deve permanecer inalterado.
- O modo batch de multiplos arquivos ainda nao existe no Bronze e e exatamente a lacuna a ser entregue.

## Contexto tecnico real do repo

- Shell atual de importacao: `frontend/src/pages/leads/ImportacaoPage.tsx`
- Formulario Bronze atual: `frontend/src/pages/leads/importacao/ImportacaoUploadStep.tsx`
- Cliente HTTP do upload Bronze: `frontend/src/services/leads_import.ts` -> `createLeadBatch`
- Contrato backend do lote Bronze: `backend/app/routers/leads.py` -> `criar_batch`
- Modelo persistido do lote: `backend/app/models/lead_batch.py`
- Schema de leitura do lote: `backend/app/schemas/lead_batch.py`
- Catalogo de eventos usado no upload: `GET /leads/referencias/eventos` em `backend/app/routers/leads.py`
- Criacao rapida de evento: `frontend/src/components/QuickCreateEventoModal.tsx`
- Criacao/listagem de ativacoes do evento: `frontend/src/services/eventos/workflow.ts`
- Atualizacao de evento existente: `frontend/src/services/eventos/core.ts` -> `updateEvento`
- Lista de agencias para completar evento: `frontend/src/services/agencias.ts` -> `listAgencias`
- Regras de elegibilidade para importacao por ativacao: `backend/app/services/evento_activation_import.py`
- Promocao Gold por lote: `backend/app/services/lead_pipeline_service.py`

## Objetivo

Implementar no passo inicial de `/leads/importar` um modo de **upload batch de planilhas**, em que o usuario:

- clica em um botao/acao de modo batch;
- seleciona varias planilhas `.csv`/`.xlsx` de uma vez;
- ve uma **tabela editavel** com uma linha por arquivo;
- preenche por linha os mesmos metadados hoje exigidos no upload Bronze simples;
- consegue criar evento rapidamente e criar ativacao ad hoc sem sair da tabela;
- quando seleciona um evento existente, a UI carrega automaticamente as informacoes dependentes do evento;
- quando alguma informacao relevante do evento estiver faltando para o fluxo escolhido, a propria linha exibe o dropdown/formulario pertinente para o usuario completar e seguir.

## Escopo funcional esperado

- Adicionar um modo visual `single` vs `batch` somente no fluxo Bronze.
- O fluxo ETL (`preview/commit`) deve permanecer inalterado nesta entrega.
- Cada linha do modo batch deve espelhar o contrato atual de `createLeadBatch`.
- A grade deve permitir editar varias linhas sem navegar para fora da tela.
- O nome do arquivo deve aparecer sempre na primeira coluna.
- Nao criar endpoint multi-upload no backend nesta iteracao, salvo bloqueio tecnico real documentado.

## Contrato explicito do estado por linha (modo batch)

- Estrutura minima por linha:
- `local_id`
- `file`
- `file_name`
- `quem_enviou`
- `plataforma_origem`
- `data_envio`
- `evento_id`
- `origem_lote`
- `tipo_lead_proponente`
- `ativacao_id`
- `status_ui` (`draft`, `submitting`, `created`, `error`)
- `created_batch_id`
- `error_message`

- Campos de negocio por linha (mesmo contrato Bronze atual):
- arquivo
- quem enviou
- plataforma de origem
- data de envio
- evento de referencia
- origem dos leads: `proponente` ou `ativacao`
- quando `proponente`: `tipo_lead_proponente` (`entrada_evento` ou `bilheteria`)
- quando `ativacao`: `ativacao_id` obrigatorio

- Transicoes de status por linha:
- `draft -> submitting` ao iniciar envio da linha
- `submitting -> created` quando API retorna `batch_id`
- `submitting -> error` quando API falha
- `error -> submitting` ao tentar reenviar
- `created` e terminal para aquela linha (exceto acao explicita de reset/remocao)

- Regras de validacao por linha:
- `file`, `quem_enviou`, `plataforma_origem`, `data_envio`, `evento_id` obrigatorios
- `origem_lote = proponente` exige `tipo_lead_proponente` valido
- `origem_lote = ativacao` exige `evento_id`, `ativacao_id` e evento habilitado para ativacao
- linha invalida nao entra na fila de submit

## Reuso obrigatorio dos mecanismos atuais

- Reutilizar o autocomplete de evento baseado em `listReferenciaEventos`.
- Reutilizar a experiencia de **Criar evento rapidamente** com `QuickCreateEventoModal`.
- Reutilizar `createEvento(..., criar_ativacao_padrao_bb: true)` para que novos eventos ja nascam alinhados ao fluxo atual.
- Reutilizar `listEventoAtivacoes` e `createEventoAtivacao` para a linha cujo evento ja esta escolhido.
- Reutilizar `supportsActivationImport` e `getActivationImportBlockReason` para habilitar/bloquear `origem_lote = ativacao`.
- Reutilizar `updateEvento` para completar dependencia faltante no proprio contexto da linha (caso de agencia).
- Reutilizar `listAgencias` para selecao de agencia no editor inline de evento.
- Reutilizar `createLeadBatch` para persistir cada arquivo/linha.

## Fluxo operacional por etapa (batch Bronze)

1. Usuario ativa modo `batch` no passo de upload Bronze.
2. Usuario seleciona multiplos arquivos `.csv`/`.xlsx`.
3. UI gera uma linha por arquivo com estado inicial `draft`.
4. Usuario preenche/ajusta metadados por linha sem sair da grade.
5. UI resolve dependencias por linha (evento, ativacao, pendencias de evento).
6. Usuario dispara submit batch.
7. UI valida linhas, envia somente linhas validas com concorrencia limitada e atualiza status por linha.
8. Linhas `created` exibem `batch_id` e acao para seguir no fluxo existente (`mapping/pipeline`) por lote.

## Comportamento esperado quando o evento e selecionado

- Ao selecionar um evento em uma linha, carregar do catalogo local:
- `agencia_id`
- `supports_activation_import`
- `activation_import_block_reason`
- `data_inicio_prevista`
- Se a origem da linha for `ativacao` e o evento suportar ativacao, carregar as ativacoes com `listEventoAtivacoes(evento_id)`.
- Se a origem da linha for `ativacao` e o evento nao tiver ativacoes, exibir na propria linha um estado vazio com acao **Criar ativacao**.
- Se o evento nao suportar importacao por ativacao por falta de `agencia_id`, a linha deve mostrar o motivo e impedir submit em `ativacao`.

## Completar informacoes faltantes do evento na propria tabela

- Se o usuario selecionar um evento existente e a linha precisar de informacao faltante do evento para o fluxo escolhido, mostrar editor inline na propria linha em vez de mandar o usuario embora.
- No minimo, cobrir o caso real ja existente no backend: **evento sem `agencia_id` bloqueia importacao por ativacao**.
- Para esse caso, renderizar na linha um seletor de agencia usando `listAgencias`, e ao confirmar:
- chamar `updateEvento(token, evento_id, { agencia_id })`
- atualizar o cache local daquele evento
- recalcular `supports_activation_import`
- habilitar o seletor de ativacao sem obrigar reload da pagina
- Se houver outros campos claramente necessarios para o fluxo escolhido e ja suportados pelo contrato de `updateEvento`, o implementador pode estender o editor inline, mas sem transformar esta entrega em um editor completo de evento.

## UX sugerida

- Adicionar um botao ou toggle visivel no Upload Bronze:
- `Upload simples`
- `Upload batch`

- No modo batch:
- botao para selecionar multiplos arquivos
- tabela com uma linha por arquivo
- validacoes inline por celula/linha
- acoes por linha:
- criar evento rapidamente
- criar ativacao
- completar agencia do evento, quando faltar
- remover linha

- A tabela pode ter colunas como:
- Arquivo
- Quem enviou
- Plataforma
- Data envio
- Evento
- Origem
- Tipo proponente / Ativacao
- Pendencias
- Status

- E desejavel permitir preenchimento inicial padrao para varias linhas:
- `quem_enviou` default com `user.email`
- `data_envio` default com hoje
- opcional: acoes de "aplicar a todas as linhas selecionadas" para reduzir digitacao

## Algoritmo operacional de submit batch

- Validar todas as linhas antes de iniciar qualquer request.
- Marcar como elegiveis apenas linhas sem erro de validacao.
- Executar envios com concorrencia limitada para evitar timeout e manter feedback previsivel.
- Exemplo aceitavel: sequencial ou concorrencia limitada em 2-4 requests.
- Para cada linha elegivel:
- setar `status_ui = submitting`
- chamar `createLeadBatch` com payload daquela linha
- em sucesso: `status_ui = created`, `created_batch_id = response.id`, `error_message = null`
- em falha: `status_ui = error`, `error_message = mensagem da API`
- Nao aplicar rollback global se uma linha falhar.
- Preservar resultados de linhas bem sucedidas.
- Exibir resumo final por linha (created/error) sem perder estado da grade.

```ts
// Pseudocodigo de referencia
const validRows = rows.filter(validateRow);
await promisePool(validRows, concurrencyLimit, async (row) => {
  updateRow(row.local_id, { status_ui: "submitting", error_message: null });
  try {
    const batch = await createLeadBatch(token, toPayload(row));
    updateRow(row.local_id, { status_ui: "created", created_batch_id: batch.id });
  } catch (err) {
    updateRow(row.local_id, { status_ui: "error", error_message: toApiErrorMessage(err) });
  }
});
```

## Pos-submit e integracao com o fluxo atual

- Como o restante da arquitetura continua centrado em `batch_id`, a versao batch deve **reaproveitar o fluxo atual de mapeamento/pipeline por lote**.
- Depois de criar os lotes, cada linha criada deve oferecer ao menos uma acao para:
- abrir o mapeamento daquele lote no shell atual (`/leads/importar?step=mapping&batch_id=<id>`)
- visualizar preview do lote, se fizer sentido na UX final
- Nao tentar resolver nesta entrega um "mapeamento unificado de varios arquivos ao mesmo tempo" se isso exigir reescrever o contrato Silver/Gold.
- O v1 aceitavel e:
- batch para cadastrar e subir varios arquivos para Bronze
- cada arquivo segue depois no pipeline existente por `batch_id`

## Regras de negocio que precisam ser preservadas

- `origem_lote = ativacao` exige:
- `evento_id`
- `ativacao_id`
- `ativacao_id` pertencendo ao `evento_id`
- evento com `agencia_id`, conforme regra atual

- `origem_lote = proponente` aceita:
- `tipo_lead_proponente = entrada_evento` ou `bilheteria`

- A promocao Gold ja distingue corretamente:
- batch de ativacao -> cria/reusa `AtivacaoLead` e chama `ensure_lead_event(..., source_kind=ACTIVATION, source_ref_id=ativacao_lead.id)`
- batch de proponente -> usa `ensure_lead_event(..., source_kind=LEAD_BATCH, source_ref_id=batch.id, tipo_lead=...)`

- Portanto, a UI batch deve respeitar exatamente esses contratos e nao introduzir novos significados para origem/tipo.

## Regras de nao regressao (obrigatorias)

- Modo `single` do Bronze deve continuar funcionando sem mudanca de comportamento.
- Fluxo ETL (`preview/commit`) deve permanecer inalterado.
- Shell canonico `/leads/importar` deve continuar sendo o ponto unico de navegacao.
- Reuso de `QuickCreateEventoModal` e servicos atuais e obrigatorio.
- Nao criar endpoint backend multi-upload nesta iteracao.

## Arquitetura de componentes sugerida

- Extrair o modo batch em componentes proprios em vez de inflar ainda mais `ImportacaoUploadStep.tsx`.
- Sugestao de estrutura:
- `frontend/src/pages/leads/importacao/batch/BatchUploadTable.tsx`
- `frontend/src/pages/leads/importacao/batch/BatchUploadRow.tsx`
- `frontend/src/pages/leads/importacao/batch/useBatchUploadDraft.ts`
- `frontend/src/pages/leads/importacao/batch/InlineEventoAgencyEditor.tsx`
- Manter `ImportacaoPage.tsx` como orquestrador de alto nivel.
- Nao duplicar `QuickCreateEventoModal`.

## Testes minimos obrigatorios (matriz verificavel)

- FE-01: selecionar varios arquivos cria varias linhas na grade.
- FE-02: linha em `proponente` envia `tipo_lead_proponente`.
- FE-03: linha em `ativacao` bloqueia sem `ativacao_id`.
- FE-04: selecionar evento carrega ativacoes da linha correta.
- FE-05: evento sem ativacoes permite criar ativacao ad hoc e prosseguir.
- FE-06: evento sem agencia mostra editor inline de agencia, salva com `updateEvento` e desbloqueia `ativacao`.
- FE-07: submit batch chama `createLeadBatch` uma vez por linha valida.
- FE-08: erros de uma linha nao apagam o estado das outras.
- FE-09: linha criada guarda `batch_id` e oferece acao para abrir o mapping atual.
- FE-10: concorrencia limitada nao bloqueia feedback de status por linha.
- FE-11: retry de linha em erro reenvia somente aquela linha.
- FE-12: modo single e fluxo ETL seguem intactos.

- BE-01: se implementacao ficar so no frontend, nao criar mudancas de backend sem necessidade.
- BE-02: se houver ajuste backend inevitavel, cobrir com teste de rota/schema.

## Criterios de aceite

- Usuario consegue selecionar varias planilhas em um unico fluxo de upload Bronze.
- Cada arquivo aparece como uma linha editavel com os metadados do fluxo atual.
- Criacao rapida de evento continua funcionando no contexto da linha.
- Se o evento existir, as dependencias da linha sao carregadas automaticamente.
- Se faltar `agencia_id` para importacao por ativacao, a propria linha permite completar isso e seguir sem sair da tela.
- Se nao houver ativacoes, a propria linha permite criar uma ativacao ad hoc e seguir.
- O submit cria um `LeadBatch` por arquivo, preservando a arquitetura atual.
- Cada linha criada pode seguir para o mapping/pipeline existente via `batch_id`.

## Fora de escopo nesta iteracao

- Novo endpoint backend que recebe varios arquivos em uma unica request.
- Novo modelo pai tipo "super lote" ou "batch de batches".
- Reescrever o fluxo Silver/Gold para operar em varios arquivos simultaneamente sob um unico `batch_id`.
- Unificar o mapeamento de varios arquivos heterogeneos em uma unica tela de mapping, salvo se o implementador conseguir provar que isso cai no colo da arquitetura atual sem aumento relevante de risco.

## Checklist de cobertura 1:1 (preservacao sem perda)

- Decisao arquitetural principal preservada.
- Contexto tecnico real preservado.
- Objetivo funcional preservado.
- Escopo funcional esperado preservado.
- Campos por linha preservados e detalhados em contrato explicito.
- Reuso obrigatorio preservado (incluindo `createLeadBatch`, `listReferenciaEventos`, `listEventoAtivacoes`, `createEventoAtivacao`, `supportsActivationImport`, `getActivationImportBlockReason`, `updateEvento`, `listAgencias`).
- Comportamento por evento selecionado preservado.
- Completar agencia inline preservado.
- UX sugerida preservada.
- Submit batch preservado e detalhado em algoritmo operacional.
- Integracao pos-submit por `batch_id` preservada.
- Regras de negocio preservadas.
- Arquitetura sugerida preservada.
- Testes minimos preservados e convertidos em matriz acionavel.
- Criterios de aceite preservados.
- Fora de escopo preservado.

## Observacao final ao implementador

- A entrega deve ser **incremental e aderente ao desenho atual**.
- Se houver necessidade de escolher entre "arquitetura perfeita" e "encaixe limpo no fluxo existente", prefira o encaixe limpo.
- Antes de patchar, leia de ponta a ponta:
- `frontend/src/pages/leads/ImportacaoPage.tsx`
- `frontend/src/pages/leads/importacao/ImportacaoUploadStep.tsx`
- `frontend/src/services/leads_import.ts`
- `frontend/src/components/QuickCreateEventoModal.tsx`
- `frontend/src/services/eventos/workflow.ts`
- `frontend/src/services/eventos/core.ts`
- `backend/app/routers/leads.py`
- `backend/app/services/lead_pipeline_service.py`

Nota de continuidade: esta versao revisada substitui a anterior com os mesmos requisitos de negocio e com maior precisao operacional para implementacao.
